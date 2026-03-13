#define CIMGUI_DEFINE_ENUMS_AND_STRUCTS
#include <jni.h>

extern "C" {
#include "dcimgui.h"
#include "backends/dcimgui_impl_opengl2.h"
}

extern "C" {

JNIEXPORT void JNICALL
Java_imgui_ImGui_createContext(JNIEnv*, jclass)
{
    ImGui_CreateContext(NULL);
}

JNIEXPORT void JNICALL
Java_imgui_ImGui_newFrame(JNIEnv*, jclass)
{
    cImGui_ImplOpenGL2_NewFrame();
    ImGui_NewFrame();
}

JNIEXPORT void JNICALL
Java_imgui_ImGui_render(JNIEnv*, jclass)
{
    ImGui_Render();
    cImGui_ImplOpenGL2_RenderDrawData(ImGui_GetDrawData());
}

JNIEXPORT void JNICALL
Java_imgui_ImGui_begin(JNIEnv* env, jclass, jstring title)
{
    const char* str = env->GetStringUTFChars(title, 0);
    ImGui_Begin(str, NULL, 0);
    env->ReleaseStringUTFChars(title, str);
}

JNIEXPORT void JNICALL
Java_imgui_ImGui_end(JNIEnv*, jclass)
{
    ImGui_End();
}

JNIEXPORT jboolean JNICALL
Java_imgui_ImGui_button(JNIEnv* env, jclass, jstring label)
{
    const char* str = env->GetStringUTFChars(label, 0);

    bool pressed = ImGui_ButtonEx(str, (ImVec2){0,0});

    env->ReleaseStringUTFChars(label, str);

    return pressed;
}

JNIEXPORT void JNICALL Java_imgui_ImGui_setDisplaySize(JNIEnv*, jclass, jfloat w, jfloat h)
{
    ImGui_GetIO()->DisplaySize = (ImVec2){w, h};
}

JNIEXPORT void JNICALL Java_imgui_ImGui_initOpenGL2(JNIEnv*, jclass)
{
    cImGui_ImplOpenGL2_Init();
}

JNIEXPORT void JNICALL Java_imgui_ImGui_shutdownOpenGL2(JNIEnv*, jclass)
{
    cImGui_ImplOpenGL2_Shutdown();
}

JNIEXPORT void JNICALL Java_imgui_ImGui_showDemoWindow(JNIEnv* env, jclass, jbooleanArray p_open)
{
    // Step 1: get a C pointer into the Java array
    jboolean* buf = env->GetBooleanArrayElements(p_open, 0);

    // Step 2: call imgui, casting jboolean* to bool*
    ImGui_ShowDemoWindow((bool*)buf);

    // Step 3: write changes back to Java and release
    env->ReleaseBooleanArrayElements(p_open, buf, 0);
}

JNIEXPORT void JNICALL Java_imgui_ImGui_addKeyEvent(JNIEnv*, jclass, jint imguiKey, jboolean down)
{
    ImGuiIO_AddKeyEvent(ImGui_GetIO(), (ImGuiKey)imguiKey, (bool)down);
}

JNIEXPORT void JNICALL Java_imgui_ImGui_addCharEvent(JNIEnv*, jclass, jint c)
{
    ImGuiIO_AddInputCharacter(ImGui_GetIO(), (unsigned int)c);
}

JNIEXPORT void JNICALL Java_imgui_ImGui_addMouseWheelEvent(JNIEnv*, jclass, jfloat x, jfloat y)
{
    ImGuiIO_AddMouseWheelEvent(ImGui_GetIO(), x, y);
}

JNIEXPORT jboolean JNICALL Java_imgui_ImGui_wantCaptureKeyboard(JNIEnv*, jclass)
{
    return (jboolean)ImGui_GetIO()->WantCaptureKeyboard;
}

JNIEXPORT jboolean JNICALL Java_imgui_ImGui_wantCaptureMouse(JNIEnv*, jclass)
{
    return (jboolean)ImGui_GetIO()->WantCaptureMouse;
}

JNIEXPORT void JNICALL Java_imgui_ImGui_setMousePos(JNIEnv*, jclass, jfloat x, jfloat y)
{
    ImGuiIO_AddMousePosEvent(ImGui_GetIO(), x, y);
}

JNIEXPORT void JNICALL Java_imgui_ImGui_setMouseButton(JNIEnv*, jclass, jint btn, jboolean down)
{
    ImGuiIO_AddMouseButtonEvent(ImGui_GetIO(), btn, (bool)down);
}

}