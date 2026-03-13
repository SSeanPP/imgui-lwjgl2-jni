# imgui-lwjgl2-jni

JNI bindings for [Dear ImGui](https://github.com/ocornut/imgui) targeting **Java 1.6** and **LWJGL 2.9.3** (legacy OpenGL2).

&#x20;

## Why does this exist?

Dear ImGui has bindings for almost every language and framework — except legacy Java. If you're building on top of LWJGL 2 (Minecraft-era OpenGL, Java 1.6), there is nothing. This project fills that gap.

The pipeline works like this:

```
imgui.h  ──►  dear\_bindings  ──►  dcimgui.h / dcimgui.cpp  (C API)
                                         │
                                   imgui\_jni.cpp  (JNI wrapper)
                                         │
                                   imgui\_jni.dll / .so / .dylib
                                         │
                                   ImGui.java  ──►  imgui-lwjgl2-jni.jar
```

A single build script handles all of it — cloning dependencies, generating C bindings, compiling the native library, and packaging the Java jar.

&#x20;

## Current bindings

This is a young project — only what is listed here is wrapped and verified working. Contributions welcome.

**Lifecycle:** `createContext` / `destroyContext` / `initOpenGL2` / `shutdownOpenGL2` / `newFrame` / `render`

**Windows:** `begin` / `end`

**Widgets:** `button` / `showDemoWindow`

**Display:** `setDisplaySize`

**Input — raw events (feed these from your render loop):**

* `setMousePos(float x, float y)`
* `setMouseButton(int button, boolean down)`
* `addMouseWheelEvent(float x, float y)`
* `addKeyEvent(int imguiKey, boolean down)`
* `addCharEvent(int c)`

**Input — intent flags (read these to gate your game's own input handling):**

* `wantCaptureKeyboard()` — true when a text field or other keyboard widget has focus
* `wantCaptureMouse()` — true when the mouse is over any ImGui window

**Build:** Windows `.dll`, Linux `.so`, macOS `.dylib` — one script, no manual cmake.

&#x20;

## Requirements

|Tool|Version|Notes|
|-|-|-|
|Python|3.10+|For build script and dear\_bindings|
|JDK|1.6 – 1.8|JDK 9+ cannot target Java 6|
|g++|64-bit|w64devkit on Windows, system gcc elsewhere|
|git|any|For cloning imgui and dear\_bindings|

**Windows:** Install [w64devkit](https://github.com/skeeto/w64devkit/releases) and add it to the front of your PATH.
If you have multiple g++ versions installed, set `GXX` to point at the right one:

```powershell
$env:GXX = "C:\\Program Files\\w64devkit\\bin\\g++.exe"
```

&#x20;

## Building

**1. Clone this repo**

```bash
git clone https://github.com/yourname/imgui-lwjgl2-jni.git
cd imgui-lwjgl2-jni
```

**2. Drop your LWJGL 2.9.3 jar into `lib/`**

```
lib/lwjgl.jar
```

LWJGL 2.9.3 can be downloaded from the [LWJGL 2 archive](https://sourceforge.net/projects/java-game-lib/).

**3. Set JAVA\_HOME to your JDK**

```powershell
# Windows
$env:JAVA\_HOME = "C:\\Program Files\\Java\\jdk1.8.0\_XXX"

# Linux / macOS
export JAVA\_HOME=/usr/lib/jvm/java-8-openjdk-amd64
```

**4. Run the build script**

```bash
python build.py
```

The script will:

* Clone [imgui](https://github.com/ocornut/imgui) and [dear\_bindings](https://github.com/dearimgui/dear_bindings) into `src/` if they aren't there
* Generate the C API bindings
* Compile the native library
* Package `imgui-lwjgl2-jni.jar`

Outputs land in `out/`:

```
out/
├── imgui\_jni.dll          (or .so / .dylib)
└── imgui-lwjgl2-jni.jar
```

**Build flags:**

```bash
python build.py --skip-bindings   # skip dear\_bindings generation
python build.py --skip-compile    # skip native library compilation
python build.py --skip-jar        # skip JAR compilation
```

&#x20;

## Usage

Add `imgui-lwjgl2-jni.jar` to your classpath and place the native library somewhere on `java.library.path`.

```java
package imgui;

import org.lwjgl.opengl.Display;
import org.lwjgl.opengl.DisplayMode;
import org.lwjgl.opengl.GL11;
import org.lwjgl.input.Mouse;
import org.lwjgl.input.Keyboard;

public class MyApp {
    public static void main(String\[] args) throws Exception {
        // 1. Create window first
        Display.setDisplayMode(new DisplayMode(1280, 720));
        Display.create();

        // 2. Init ImGui after GL context exists
        ImGui.createContext();
        ImGui.initOpenGL2();

        boolean\[] open = { true };

        while (!Display.isCloseRequested()) {
            GL11.glClear(GL11.GL\_COLOR\_BUFFER\_BIT);

            // Feed input to ImGui
            ImInput.handleMouseAndScroll();
            while (Keyboard.next()) {
                ImInput.handleKeyboardEvent(
                    Keyboard.getEventKeyState(),
                    Keyboard.getEventKey()
                );
            }

            // Your game input — only if ImGui doesn't want it
            if (!ImGui.wantCaptureKeyboard()) {
                // handle game keys
            }

            ImGui.newFrame();

            ImGui.begin("Debug", 0);
            ImGui.text("Hello from ImGui!");
            if (ImGui.button("Click", 0, 0)) {
                System.out.println("clicked");
            }
            ImGui.end();

            ImGui.render();

            Display.update();
            Display.sync(60);
        }

        ImGui.shutdownOpenGL2();
        ImGui.destroyContext();
        Display.destroy();
    }
}
```

&#x20;

## Project structure

```
imgui-lwjgl2-jni/
├── build.py                  # Full build pipeline
├── src/
│   ├── imgui\_jni.cpp         # JNI wrapper — add new bindings here
│   ├── dcimgui\_impl.cpp      # dear\_bindings impl glue
│   ├── imgui/                # submodule: ocornut/imgui
│   ├── dear\_bindings/        # submodule: dearimgui/dear\_bindings
│   └── java/
│       └── imgui/
│           ├── ImGui.java    # Native method declarations
│           └── ImInput.java  # LWJGL 2 input helpers
├── lib/
│   └── lwjgl.jar             # You provide this
└── out/                      # Build outputs (gitignored)
```

&#x20;

## ImInput — LWJGL 2 input helper

`ImInput` bridges LWJGL 2's event-based input system to ImGui. LWJGL 2 uses its own key constants (`Keyboard.KEY\_A` etc) while ImGui uses its own `ImGuiKey` enum — `ImInput` maintains the mapping between them and handles the translation.

It provides three methods:

* `ImInput.handleMouseAndScroll()` — reads current mouse position (flipping Y since LWJGL and ImGui have opposite Y origins), left/right button state, and scroll wheel, then forwards all of it to ImGui. Call this once per frame before `newFrame()`.
* `ImInput.handleKeyboardEvent(boolean down, int lwjglKey)` — translates a single LWJGL key event to an ImGui key event and forwards it. Also sends the typed character via `addCharEvent` so text fields work correctly. Call this inside your `while (Keyboard.next())` loop before `newFrame()`.
* `ImInput.toImGui(int lwjglKey)` — raw key mapping lookup, returns -1 if the key has no ImGui equivalent. Use this if you want to handle forwarding yourself rather than using `handleKeyboardEvent`.

The pattern in your render loop:

```java
// Before newFrame() — feed all input to ImGui
ImInput.handleMouseAndScroll();
while (Keyboard.next()) {
    ImInput.handleKeyboardEvent(Keyboard.getEventKeyState(), Keyboard.getEventKey());
}

ImGui.newFrame();

// After newFrame() — gate your game's input on ImGui's intent flags
if (!ImGui.wantCaptureKeyboard()) {
    // your game keyboard handling here
}
if (!ImGui.wantCaptureMouse()) {
    // your game mouse handling here
}
```

ImGui always receives the events — `wantCaptureKeyboard` and `wantCaptureMouse` tell you whether ImGui actually consumed them so your game knows whether to act on them too.

&#x20;

## Adding new bindings

Not every ImGui function is wrapped yet. To add a function:

**1. Find the C signature in `src/dear\_bindings/generated/dcimgui.h`:**

```c
CIMGUI\_API void ImGui\_TextColored(ImVec4 col, const char\* fmt);
```

**2. Add the JNI wrapper to `src/imgui\_jni.cpp`:**

```cpp
JNIEXPORT void JNICALL Java\_imgui\_ImGui\_textColored(
    JNIEnv\* env, jclass,
    jfloat r, jfloat g, jfloat b, jfloat a,
    jstring text)
{
    const char\* str = env->GetStringUTFChars(text, 0);
    ImGui\_TextColored((ImVec4){r, g, b, a}, "%s", str);
    env->ReleaseStringUTFChars(text, str);
}
```

**3. Add the Java declaration to `src/java/imgui/ImGui.java`:**

```java
public static native void textColored(float r, float g, float b, float a, String text);
```

**4. Rebuild:**

```bash
python build.py --skip-bindings
```

`ImVec2` and `ImVec4` args are split into individual floats since Java has no struct equivalent. `bool\*` args become `boolean\[]` of length 1 so the value can be modified in place.

Contributions for additional wrapped functions are welcome — see [issues](https://github.com/yourname/imgui-lwjgl2-jni/issues) for the current tracking list of unwrapped functions.

&#x20;

## Known limitations

* Functions taking `void\*`, function pointers, or `ImDrawList\*` are not wrapped — these require more complex bridging
* `InputText` with callbacks is not supported yet
* No multi-context support
* Tested on Windows only so far — Linux and macOS builds are implemented but unverified

&#x20;

## License

The JNI bindings and build script in this repo are MIT licensed.
Dear ImGui and dear\_bindings carry their own MIT licenses.
LWJGL 2 is BSD licensed.

