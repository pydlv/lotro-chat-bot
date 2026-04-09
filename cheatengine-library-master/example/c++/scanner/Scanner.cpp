// Scanner.cpp
// Small application to demonstrate how to scan using CheatEngine API
// DISCLAIMER:	This was used to learn how to interact with the API using c++.
//				there is minimal error checking and minimal input options.

#include "Connector.hpp"
#include <iostream>
#include <comutil.h>
#include <Windows.h>
#include <Commctrl.h>
#include <locale>
#include <codecvt>
#include <tlhelp32.h>
#include <vector>
#include <sstream>
#include <exception>
#include <assert.h>

#define IDC_TESTCHEATENGWINDOW 109

using convert_type = std::codecvt_utf8<wchar_t>;
std::wstring_convert<convert_type, wchar_t> converter;

const int wm_scandone = 0x8000 + 2;

bool unicode;
bool casesensitive;
TVariableType varopt;
TScanOption scanopt;
TFastScanMethod fastscanmethod;
Tscanregionpreference writable, executable, copyOnWrite;
bstr_t processStr;
bstr_t value1, value2;
bstr_t startscan;
bstr_t endscan;
bstr_t alignment;

/// <summary>
/// Helper to convert BSTR to std::string.
/// </summary>
std::string BstrToStr(BSTR bs)
{
	assert(bs != nullptr);
	std::wstring ws(bs, SysStringLen(bs));
	std::string str = converter.to_bytes(ws);
	return str;
}

LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
	switch (message)
	{
	case wm_scandone:
	{
		std::cout << "scan complete!" << std::endl;
		int size = iGetBinarySize();
		if (varopt == TVariableType::vtString)
			if (unicode)
				iInitFoundList(varopt, size / 16, false, false, false, unicode);
			else
				iInitFoundList(varopt, size / 8, false, false, false, unicode);
		else
			iInitFoundList(varopt, size, false, false, false, unicode);

		if (scanopt != TScanOption::soUnknownValue)
		{
			long long found = min((int)iCountAddressesFound(), 10000000);
			std::cout << "found: " << found << std::endl;

			for (long long i = 0; i < found; i++)
			{
				BSTR address, value;
				iGetAddress(i, address, value);
				std::cout << "address: " << BstrToStr(address) << ", value: " << BstrToStr(value) << std::endl;
			}
		}
		break;
	}
	default: // don't need anything else from our fake window
		return DefWindowProc(hWnd, message, wParam, lParam);
	}
	return 0;
}

void displayProcesses()
{
	BSTR processList;
	iGetProcessList(processList);
	std::cout << BstrToStr(processList) << std::endl;
}

template<class T>
std::string ToHex(const T &value)
{
	std::ostringstream oss;
	if (!(oss << std::hex << value))throw std::exception("Invalid argument");
	return oss.str();
}

//placeholder function to get the options. Replace this with however complex of a method you like.
void getOptions(TScanOption& scanopt, TVariableType& varopt, bstr_t& value1,
	Tscanregionpreference writable, Tscanregionpreference executable, Tscanregionpreference  copyOnWrite,
	bstr_t& value2, bstr_t& startscan, bstr_t& endscan, bool& unicode, bool& casesensitive,
	TFastScanMethod& fastscanmethod, bstr_t& alignment, bstr_t& processStr)
{
	unicode = false;
	casesensitive = false;
	varopt = TVariableType::vtDouble;
	scanopt = TScanOption::soExactValue;

	fastscanmethod = TFastScanMethod::fsmAligned;
	writable = Tscanregionpreference::scanInclude;
	executable = Tscanregionpreference::scanDontCare;
	copyOnWrite = Tscanregionpreference::scanExclude;


	/* Grab the process ID */
	/* http://en.ciholas.fr/get-process-id-pid-from-process-name-string-c-windows-api/ */

	DWORD pid = 0;
	std::wstring targetProcessName = L"lotroclient.exe";

	HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0); //all processes

	PROCESSENTRY32W entry; //current process
	entry.dwSize = sizeof entry;

	if (!Process32FirstW(snap, &entry)) { //start with the first in snapshot
		std::cout << "No process found." << std::endl;
		exit(0);
	}

	do {
		if (std::wstring(entry.szExeFile) == targetProcessName) {
			pid = entry.th32ProcessID; //name matches; add to list
		}
	} while (Process32NextW(snap, &entry)); //keep going until end of snapshot

	std::string inputProcess;
	inputProcess = ToHex(pid);

	std::cout << "PID of LOTRO: " << std::hex << pid << std::endl;

	if (pid == 0) {
		std::cout << "No process found." << std::endl;
		exit(0);
	}

	// std::cout << "Type process ID (hex): ";
	// std::cin >> inputProcess;

	processStr = inputProcess.c_str();

	std::string inputVal;

	// std::cout << "Type value to search (double): ";
	// std::cin >> inputVal;
	inputVal = "29382838";

	value1 = inputVal.c_str();
	value2 = "";

	startscan = "$0000000000000000";
	endscan = "$7fffffffffffffff";

	alignment = "1";
}

void setupFakeWindow(HWND& hWnd, HMODULE& hInstance)
{
	hInstance = GetModuleHandle(NULL);
	static TCHAR szWindowClass[] = _T("win32app");

	WNDCLASSEX wcex;

	wcex.cbSize = sizeof(WNDCLASSEX);

	wcex.style = CS_HREDRAW | CS_VREDRAW;
	wcex.lpfnWndProc = WndProc;
	wcex.cbClsExtra = 0;
	wcex.cbWndExtra = 0;
	wcex.hInstance = hInstance;
	wcex.hIcon = LoadIcon(NULL, IDI_APPLICATION);
	wcex.hIconSm = LoadIcon(NULL, IDI_APPLICATION);
	wcex.hCursor = LoadCursor(nullptr, IDC_ARROW);
	wcex.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
	wcex.lpszMenuName = NULL;
	wcex.lpszClassName = szWindowClass;

	auto classReg = RegisterClassEx(&wcex);

	static TCHAR szTitle[] = _T("Test");

	hWnd = CreateWindow(
		szWindowClass,
		szTitle,
		WS_OVERLAPPEDWINDOW,
		CW_USEDEFAULT, CW_USEDEFAULT,
		500, 100,
		NULL,
		NULL,
		hInstance,
		NULL
	);
}

//Standard message loop
void messageLoop(HMODULE& hInstance)
{
	HACCEL hAccelTable = LoadAccelerators(hInstance, MAKEINTRESOURCE(IDC_TESTCHEATENGWINDOW));

	MSG msg;

	while (GetMessage(&msg, nullptr, 0, 0))
	{
		if (!TranslateAccelerator(msg.hwnd, hAccelTable, &msg))
		{
			TranslateMessage(&msg);
			DispatchMessage(&msg);
		}
	}
}

int main()
{
	//either 32 or 64 bit should match your compile
#ifdef _M_X64
	auto libInst = LoadLibrary("ce-lib64.dll");
#else
	auto libInst = LoadLibrary("ce-lib32.dll");
#endif

	if (libInst == NULL)
	{
		int code = GetLastError();
		std::cout << "Error loading ce-lib64.dll, Error number: " << code << std::endl;
		std::cin.get(); //wait before closing
		return code;
	}
	else
	{
		//load all functions from dll
		loadFunctions(libInst);

		HWND hWnd;
		HMODULE hInstance;

		//need fake window for cheat engine to send messages to WndProc
		setupFakeWindow(hWnd, hInstance);

		if (hWnd == NULL)
		{
			int code = GetLastError();
			std::cout << "Couldn't create window. Error Code: " << code << std::endl;
			std::cin.get(); //wait before closing
			return code;
		}

		getOptions(scanopt, varopt, value1, writable, executable, copyOnWrite, value2,
			startscan, endscan, unicode, casesensitive, fastscanmethod, alignment, processStr);

		//open running process by pid
		iOpenProcess(processStr);
		//tell cheat engine where to send messages
		iInitMemoryScanner(hWnd);
		//set up the scanner
		iConfigScanner(writable, executable, copyOnWrite);

		std::cout << "Starting first scan.";

		//execute scan
		iFirstScan(scanopt, varopt, TRoundingType::rtRounded, value1,
			value2, startscan, endscan, false, false, unicode, casesensitive,
			fastscanmethod, alignment);

		//run message loop so we can recieve scan complete message
		messageLoop(hInstance);
	}
	return 0;
}


