package imgui;

public class ImGui {
    static {
        System.loadLibrary("imgui_jni");
    }

    public static native void createContext();
    public static native void newFrame();
    public static native void render();
    public static native void begin(String title);
    public static native void end();
    public static native boolean button(String label);
    public static native void setDisplaySize(float width, float height);
    public static native void initOpenGL2();
    public static native void shutdownOpenGL2();
    public static native void setMousePos(float x, float y);
    public static native void setMouseButton(int button, boolean down);
    public static native void showDemoWindow(boolean[] pOpen);
    public static native void addKeyEvent(int imguiKey, boolean down);
    public static native void addCharEvent(int c);
    public static native void addMouseWheelEvent(float x, float y);
    public static native boolean wantCaptureKeyboard();
    public static native boolean wantCaptureMouse();
}