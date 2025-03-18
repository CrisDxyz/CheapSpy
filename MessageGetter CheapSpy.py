import win32gui
import win32con
import win32ui
import ctypes

messages = []  # Live messages
unique_messages = {}  # Stores different values permanently
scroll_offset = 0  # Keeps track of scrolling

user32 = ctypes.windll.user32  # Load user32.dll

def categorize_message(msg):
    """Categorizes messages into meaningful groups."""
    if msg in [win32con.WM_KEYDOWN, win32con.WM_KEYUP, win32con.WM_CHAR]:
        return "Keyboard Input"
    elif msg in [win32con.WM_LBUTTONDOWN, win32con.WM_LBUTTONUP, win32con.WM_MOUSEMOVE]:
        return "Mouse Interaction"
    elif msg in [win32con.WM_MOVE, win32con.WM_SIZE, win32con.WM_SETFOCUS, win32con.WM_KILLFOCUS]:
        return "Window Event"
    return "Unknown Message"

def wndproc(hwnd, message, wparam, lparam):
    global messages, unique_messages, scroll_offset

    if message == win32con.WM_TIMER:  # Timer event for updating window
        win32gui.InvalidateRect(hwnd, None, True)
        return 0

    elif message == win32con.WM_MOUSEWHEEL:
        delta = ctypes.c_short(wparam >> 16).value  # Extract scroll direction
        scroll_offset -= delta // 120 * 20  # Adjust scroll step
        scroll_offset = max(scroll_offset, 0)  # Prevent scrolling too high
        win32gui.InvalidateRect(hwnd, None, True)
        return 0

    # Store live messages (last 10)
    msg_info = f"Msg: {message} | wParam: {wparam} | lParam: {lparam}"
    messages.append(msg_info)
    if len(messages) > 10:
        messages.pop(0)

    # Store unique messages with wParam (e.g., keyboard keycode)
    key = (message, wparam)  # Unique key (message type + wParam)
    if key not in unique_messages:
        unique_messages[key] = (msg_info, categorize_message(message))

    if message == win32con.WM_PAINT:
        hdc, ps = win32gui.BeginPaint(hwnd)
        hdc = win32ui.CreateDCFromHandle(hdc)

        font = win32ui.CreateFont({"name": "Consolas", "height": 18})
        hdc.SelectObject(font)

        y = 20 - scroll_offset  # Apply scrolling offset

        # Draw live messages
        hdc.TextOut(10, y, "[Live Events]")
        y += 20
        for msg in messages:
            hdc.TextOut(10, y, msg)
            y += 20

        # Draw unique message log
        y += 20
        hdc.TextOut(10, y, "[Unique Events]")
        y += 20
        for (msg, wparam), (desc, category) in unique_messages.items():
            hdc.TextOut(10, y, f"{category}: {desc}")
            y += 20

        win32gui.EndPaint(hwnd, ps)
        return 0

    elif message == win32con.WM_DESTROY:
        user32.KillTimer(hwnd, 1)  # Stop timer
        win32gui.PostQuitMessage(0)
        return 0

    return win32gui.DefWindowProc(hwnd, message, wparam, lparam)

class_name = "MessageLoggerWindow"
hInstance = win32gui.GetModuleHandle(None)

wndclass = win32gui.WNDCLASS()
wndclass.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
wndclass.lpfnWndProc = wndproc
wndclass.hInstance = hInstance
wndclass.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
wndclass.hbrBackground = win32con.COLOR_WINDOW + 1
wndclass.lpszClassName = class_name

atom = win32gui.RegisterClass(wndclass)

hwnd = win32gui.CreateWindow(
    atom,
    "Windows Message Logger CheapSpy",
    win32con.WS_OVERLAPPEDWINDOW,
    100, 100, 600, 400,
    0, 0, hInstance, None
)

user32.SetTimer(hwnd, 1, 100, None)  # Use ctypes to call SetTimer()

win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
win32gui.UpdateWindow(hwnd)
win32gui.PumpMessages()
