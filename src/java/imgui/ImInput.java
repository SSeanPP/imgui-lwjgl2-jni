package imgui;

import org.lwjgl.input.Keyboard;
import org.lwjgl.input.Mouse;
import org.lwjgl.opengl.Display;

public class ImInput {
	// ImGuiKey values — must match dcimgui.h ImGuiKey enum
    // Check your dcimgui.h for the exact values if these are wrong
    public static final int ImGuiKey_Tab        = 512;
    public static final int ImGuiKey_LeftArrow  = 513;
    public static final int ImGuiKey_RightArrow = 514;
    public static final int ImGuiKey_UpArrow    = 515;
    public static final int ImGuiKey_DownArrow  = 516;
    public static final int ImGuiKey_PageUp     = 517;
    public static final int ImGuiKey_PageDown   = 518;
    public static final int ImGuiKey_Home       = 519;
    public static final int ImGuiKey_End        = 520;
    public static final int ImGuiKey_Delete     = 522;
    public static final int ImGuiKey_Backspace  = 523;
    public static final int ImGuiKey_Enter      = 525;
    public static final int ImGuiKey_Escape     = 526;
    public static final int ImGuiKey_LeftCtrl   = 527;
    public static final int ImGuiKey_LeftShift  = 528;
    public static final int ImGuiKey_LeftAlt    = 529;
    public static final int ImGuiKey_A          = 546;
    public static final int ImGuiKey_C          = 548;
    public static final int ImGuiKey_V          = 567;
    public static final int ImGuiKey_X          = 569;
    public static final int ImGuiKey_Y          = 570;
    public static final int ImGuiKey_Z          = 571;

    private static final int[] LWJGL_TO_IMGUI = new int[256];

    static {
        // Default everything to -1 (unmapped)
        java.util.Arrays.fill(LWJGL_TO_IMGUI, -1);

        LWJGL_TO_IMGUI[Keyboard.KEY_TAB]        = ImGuiKey_Tab;
        LWJGL_TO_IMGUI[Keyboard.KEY_LEFT]       = ImGuiKey_LeftArrow;
        LWJGL_TO_IMGUI[Keyboard.KEY_RIGHT]      = ImGuiKey_RightArrow;
        LWJGL_TO_IMGUI[Keyboard.KEY_UP]         = ImGuiKey_UpArrow;
        LWJGL_TO_IMGUI[Keyboard.KEY_DOWN]       = ImGuiKey_DownArrow;
        LWJGL_TO_IMGUI[Keyboard.KEY_PRIOR]      = ImGuiKey_PageUp;
        LWJGL_TO_IMGUI[Keyboard.KEY_NEXT]       = ImGuiKey_PageDown;
        LWJGL_TO_IMGUI[Keyboard.KEY_HOME]       = ImGuiKey_Home;
        LWJGL_TO_IMGUI[Keyboard.KEY_END]        = ImGuiKey_End;
        LWJGL_TO_IMGUI[Keyboard.KEY_DELETE]     = ImGuiKey_Delete;
        LWJGL_TO_IMGUI[Keyboard.KEY_BACK]       = ImGuiKey_Backspace;
        LWJGL_TO_IMGUI[Keyboard.KEY_RETURN]     = ImGuiKey_Enter;
        LWJGL_TO_IMGUI[Keyboard.KEY_ESCAPE]     = ImGuiKey_Escape;
        LWJGL_TO_IMGUI[Keyboard.KEY_LCONTROL]   = ImGuiKey_LeftCtrl;
        LWJGL_TO_IMGUI[Keyboard.KEY_LSHIFT]     = ImGuiKey_LeftShift;
        LWJGL_TO_IMGUI[Keyboard.KEY_LMENU]      = ImGuiKey_LeftAlt;
        LWJGL_TO_IMGUI[Keyboard.KEY_A]          = ImGuiKey_A;
        LWJGL_TO_IMGUI[Keyboard.KEY_C]          = ImGuiKey_C;
        LWJGL_TO_IMGUI[Keyboard.KEY_V]          = ImGuiKey_V;
        LWJGL_TO_IMGUI[Keyboard.KEY_X]          = ImGuiKey_X;
        LWJGL_TO_IMGUI[Keyboard.KEY_Y]          = ImGuiKey_Y;
        LWJGL_TO_IMGUI[Keyboard.KEY_Z]          = ImGuiKey_Z;
    }
    
    public static int toImGui(int lwjglKey) {
        if (lwjglKey < 0 || lwjglKey >= LWJGL_TO_IMGUI.length) return -1;
        return LWJGL_TO_IMGUI[lwjglKey];
    }
    
    public static void handleMouseAndScroll() {
    	ImGui.setMousePos(Mouse.getX(), Display.getHeight() - Mouse.getY());
        ImGui.setMouseButton(0, Mouse.isButtonDown(0));
        ImGui.setMouseButton(1, Mouse.isButtonDown(1));
        
        int wheel = Mouse.getDWheel();
        if (wheel != 0) {
            ImGui.addMouseWheelEvent(0, wheel > 0 ? 1.0f : -1.0f);
        }
    }
    
    public static void handleKeyboardEvent(boolean state, int key) {
        int imguiKey = ImInput.toImGui(key);
        if (imguiKey != -1) {
            ImGui.addKeyEvent(imguiKey, state);
        }
        if (state) {
            char c = Keyboard.getEventCharacter();
            if (c != Keyboard.CHAR_NONE && c >= 32) {
                ImGui.addCharEvent((int) c);
            }
        }
    }
}
