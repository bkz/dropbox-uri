#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include <string>
#include <vector>

#include <windows.h>
#include <shlguid.h>
#include <shobjidl.h>
#include <atlbase.h>
#include <wininet.h>
#include <shlobj.h>

///////////////////////////////////////////////////////////////////////////////////////////////////
// Utilities.
///////////////////////////////////////////////////////////////////////////////////////////////////

static const std::vector<std::wstring>& get_argv()
{
    static bool initialized = false;
    static std::vector<std::wstring> argv;

    if (!initialized)
    {
        int nArgs = 0;

        LPWSTR* szArglist = ::CommandLineToArgvW(::GetCommandLineW(), &nArgs);
        
        if (szArglist != NULL)
        {
            for (int i = 0; i < nArgs; i++)
                argv.push_back(szArglist[i]);
        }

        ::LocalFree(szArglist);

        initialized = true;
    }

    return argv;
}

static void wide_to_multibyte(const wchar_t* pwszSrc, std::string& result)
{
	size_t len = wcslen(pwszSrc);

	size_t num_char = ::WideCharToMultiByte(
        CP_UTF8, 0, pwszSrc, len, NULL, 0, NULL, NULL) ;

	if (num_char > 0)
	{
		result.resize(num_char);
		::WideCharToMultiByte(
            CP_UTF8, 0, pwszSrc, len, 
            const_cast<char*>(result.c_str()), num_char, NULL, NULL);
	}
}

///////////////////////////////////////////////////////////////////////////////////////////////////
// Public API.
///////////////////////////////////////////////////////////////////////////////////////////////////

#define DLLEXPORT __declspec(dllexport) 

extern "C"
{
	DLLEXPORT int set_clipboard_html(const wchar_t* html, const wchar_t* text) 
	{
		int CF_HTML = ::RegisterClipboardFormat(L"HTML Format");

        std::wstring storage;
        storage.resize(wcslen(html) + 512);

        wchar_t* buf = &storage[0];
        size_t bufsize = storage.length();

		wcscpy_s(buf, bufsize,
			L"Version:0.9\r\n"
			L"StartHTML:00000000\r\n"
			L"EndHTML:00000000\r\n"
			L"StartFragment:00000000\r\n"
			L"EndFragment:00000000\r\n"
			L"<html><body>\r\n"
			L"<!--StartFragment -->\r\n");

        wcscat_s(buf, bufsize, html);
		wcscat_s(buf, bufsize, L"\r\n");
		wcscat_s(buf, bufsize,
			L"<!--EndFragment-->\r\n"
			L"</body>\r\n"
			L"</html>\r\n");

		wchar_t* ptr = wcsstr(buf, L"StartHTML");
		wsprintf(ptr+10, L"%08u", wcsstr(buf, L"<html>") - buf);
		*(ptr+10+8) = L'\r';

		ptr = wcsstr(buf, L"EndHTML");
		wsprintf(ptr+8, L"%08u", wcslen(buf));
		*(ptr+8+8) = L'\r';

		ptr = wcsstr(buf, L"StartFragment");
		wsprintf(ptr+14, L"%08u", wcsstr(buf, L"<!--StartFrag") - buf);
		*(ptr+14+8) = L'\r';

		ptr = wcsstr(buf, L"EndFragment");
		wsprintf(ptr+12, L"%08u", wcsstr(buf, L"<!--EndFrag") - buf);
		*(ptr+12+8) = L'\r';

        if (::OpenClipboard(NULL)) 
        {
            ::EmptyClipboard();
	        
            {
                std::string utf8;
                wide_to_multibyte(buf, utf8);

                HGLOBAL hTextHtml = ::GlobalAlloc(GMEM_MOVEABLE |GMEM_DDESHARE, 
                    utf8.length()+1);
                
                char* p = (char*)::GlobalLock(hTextHtml);
                strcpy_s(p, utf8.length()+1, utf8.c_str());
                ::GlobalUnlock(hTextHtml);	        

			    ::SetClipboardData(CF_HTML, hTextHtml);
                ::GlobalFree(hTextHtml);
            }

            {
                HGLOBAL hTextUnicode = ::GlobalAlloc(GMEM_MOVEABLE |GMEM_DDESHARE, 
                    sizeof(wchar_t)*(wcslen(text)+1));

                wchar_t* p = (wchar_t*)::GlobalLock(hTextUnicode);
                wcscpy_s(p, wcslen(text)+1, text);
                ::GlobalUnlock(hTextUnicode);	        

			    ::SetClipboardData(CF_UNICODETEXT, hTextUnicode);
                ::GlobalFree(hTextUnicode);
            }

	        
            ::CloseClipboard();           	        
		}

		return 0;
	}

    DLLEXPORT int create_shortcut(
		const wchar_t* source, 
		const wchar_t* destination,
		const wchar_t* working_dir, 
		const wchar_t* arguments,
		const wchar_t* description, 
		const wchar_t* icon,
		int icon_index) 
	{
		IShellLink*   pShellLink   = NULL;
		IPersistFile* pPersistFile = NULL;

		::CoInitialize(NULL);

		HRESULT hRet = ::CoCreateInstance(
			CLSID_ShellLink, 
			NULL,
			CLSCTX_INPROC_SERVER, 
			IID_IShellLink,
			reinterpret_cast<LPVOID*>(&pShellLink));

		if (FAILED(hRet))
		{
			return false;
		}

		hRet = pShellLink->QueryInterface(IID_IPersistFile,
			reinterpret_cast<LPVOID*>(&pPersistFile));
		
		if (FAILED(hRet)) 
		{
			pShellLink->Release();
			return false;
		}

		if (FAILED(pShellLink->SetPath(source))) 
		{
			pPersistFile->Release();
			pShellLink->Release();
			return false;
		}

		if (working_dir && FAILED(pShellLink->SetWorkingDirectory(working_dir))) 
		{
			pPersistFile->Release();
			pShellLink->Release();
			return false;
		}

		if (arguments && FAILED(pShellLink->SetArguments(arguments))) 
		{
			pPersistFile->Release();
			pShellLink->Release();
			return false;
		}

		if (description && FAILED(pShellLink->SetDescription(description))) 
		{
			pPersistFile->Release();
			pShellLink->Release();
			return false;
		}

		if (icon && FAILED(pShellLink->SetIconLocation(icon, icon_index))) 
		{
			pPersistFile->Release();
			pShellLink->Release();
			return false;
		}

		hRet = pPersistFile->Save(destination, TRUE);
		
		pPersistFile->Release();
		pShellLink->Release();
		
		return SUCCEEDED(hRet);
	}

    DLLEXPORT int get_unicode_argc() 
    {
        const std::vector<std::wstring>& args = get_argv();

        return args.size();
    }

    DLLEXPORT const wchar_t* get_unicode_argv(int index) 
    {
        const std::vector<std::wstring>& args = get_argv();

        if (index < args.size())
        {
            return args[index].c_str();
        }
        else
        {
            return NULL;
        }
    }

    DLLEXPORT int explore_path(const wchar_t* filename)
    {
        std::wstring args;
        args = L"explorer.exe /select,";
        args += filename;

        STARTUPINFOW si;
        PROCESS_INFORMATION pi;

        ZeroMemory(&si, sizeof(si));
        si.cb = sizeof(si);
        ZeroMemory(&pi, sizeof(pi));

        if (::CreateProcess(NULL, (wchar_t*)args.c_str(), NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi))
        {
            ::WaitForSingleObject(pi.hProcess, INFINITE);
            ::CloseHandle(pi.hProcess);
            ::CloseHandle(pi.hThread);

            return 0;
        }

        return -1;
    }

    DLLEXPORT int is_admin()
	{
		PSID AdministratorsGroup;
		SID_IDENTIFIER_AUTHORITY NtAuthority = SECURITY_NT_AUTHORITY;

		BOOL bSuccess = ::AllocateAndInitializeSid(
			&NtAuthority,
			2,
			SECURITY_BUILTIN_DOMAIN_RID,
			DOMAIN_ALIAS_RID_ADMINS,
			0, 0, 0, 0, 0, 0,
			&AdministratorsGroup);

		if (bSuccess)
		{
			if (!::CheckTokenMembership(NULL, AdministratorsGroup, &bSuccess))
			{
				bSuccess = FALSE;
			}

			::FreeSid(AdministratorsGroup);
		}

		return (bSuccess == TRUE);
	}	

    DLLEXPORT int show_info_message(const wchar_t* title, const wchar_t* msg)
    {
        ::MessageBox(HWND_DESKTOP, msg, title, MB_OK|MB_ICONINFORMATION|MB_SYSTEMMODAL|MB_SETFOREGROUND);

        return 0;
    }

    DLLEXPORT int show_warning_message(const wchar_t* title, const wchar_t* msg)
    {
        ::MessageBox(HWND_DESKTOP, msg, title, MB_OK|MB_ICONINFORMATION|MB_SYSTEMMODAL|MB_SETFOREGROUND);

        return 0;
    }

    DLLEXPORT int show_error_message(const wchar_t* title, const wchar_t* msg)
    {
        ::MessageBox(HWND_DESKTOP, msg, title, MB_OK|MB_ICONHAND|MB_SYSTEMMODAL|MB_SETFOREGROUND);

        return 0;
    }
};

///////////////////////////////////////////////////////////////////////////////////////////////////
// The End.
///////////////////////////////////////////////////////////////////////////////////////////////////
