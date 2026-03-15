#define CIMGUI_DEFINE_ENUMS_AND_STRUCTS
#include <jni.h>

extern "C" {
#include "dcimgui.h"
#include "backends/dcimgui_impl_opengl3.h"

}

extern "C" {


//Basic Context creation
JNIEXPORT void JNICALL
Java_imgui_ImGui_createContext(JNIEnv*, jclass)
{
    ImGui_CreateContext(NULL);
}

JNIEXPORT void JNICALL
Java_imgui_ImGui_newFrame(JNIEnv*, jclass)
{
    cImGui_ImplOpenGL3_NewFrame();
    ImGui_NewFrame();
}

JNIEXPORT void JNICALL
Java_imgui_ImGui_render(JNIEnv*, jclass)
{
    ImGui_Render();
    cImGui_ImplOpenGL3_RenderDrawData(ImGui_GetDrawData());
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

JNIEXPORT void JNICALL Java_imgui_ImGui_initOpenGL3(JNIEnv*, jclass)
{
    cImGui_ImplOpenGL3_Init();
}

JNIEXPORT void JNICALL Java_imgui_ImGui_shutdownOpenGL3(JNIEnv*, jclass)
{
    cImGui_ImplOpenGL3_Shutdown();
}

JNIEXPORT void JNICALL Java_imgui_ImGui_setNextWindowPos(JNIEnv* env, jclass, jfloat x, jfloat y)
{
    ImGui_SetNextWindowPos((ImVec2){x, y}, 0);
}

// Demo (proves it works + demonstrates the java array C pointer rubbish)
JNIEXPORT void JNICALL Java_imgui_ImGui_showDemoWindow(JNIEnv* env, jclass, jbooleanArray p_open)
{
    // Step 1: get a C pointer into the Java array
    jboolean* buf = env->GetBooleanArrayElements(p_open, 0);

    // Step 2: call imgui, casting jboolean* to bool*
    ImGui_ShowDemoWindow((bool*)buf);

    // Step 3: write changes back to Java and release
    env->ReleaseBooleanArrayElements(p_open, buf, 0);
}

// Keyboard + Mouse handling
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

//Actual IMGUI components of interest
JNIEXPORT void JNICALL Java_imgui_ImGui_text(JNIEnv* env, jclass, jstring label)
{
    const char* str = env->GetStringUTFChars(label, 0);
    ImGui_Text("%s", str);
    env->ReleaseStringUTFChars(label, str);
}

JNIEXPORT void JNICALL Java_imgui_ImGui_progressBar(JNIEnv* env, jclass, jfloat fraction, jstring overlay)
{
    const char* str = env->GetStringUTFChars(overlay, 0);
    ImGui_ProgressBar(fraction, (ImVec2){-1, 0}, str);
    env->ReleaseStringUTFChars(overlay, str);
}

JNIEXPORT void JNICALL Java_imgui_ImGui_separator(JNIEnv* env, jclass)
{
    ImGui_Separator();
}

}