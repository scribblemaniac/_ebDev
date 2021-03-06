REM -i and -s switches in some order in the following command should elevate to use SYSTEM account; maybe it only works on windows 7 and earlier? :

paexec \\yourComputerName -u yourUserName -p "#.#.Y0UR P@$$W0RD.#.#" -dfr cmd

REM I THINK the command to accomplish that would be (if it works on newer windows systems) :
REM paexec \\yourComputerName -u yourUserName -p "#.#.Y0UR P@$$W0RD.#.#" -s -i cmd

exit
HALP:
Usage: PAExec [\\computer[,computer2[,...] | @file]][-u user [-p psswd][-n s]
[-l][-s|-e][-x][-i [session]][-c [-f|-v] [-csrc path]][-lo path][-rlo path]
[-ods][-w directory][-d][-<priority>][-a n,n,...][-dfr] cmd [arguments]

Standard PAExec\PsExec command line options:

     -a         Separate processors on which the application can run with
                commas where 1 is the lowest numbered CPU. For example,
                to run the application on CPU 2 and CPU 4, enter:
                -a 2,4

     -c         Copy the specified program to the remote system for
                execution. If you omit this option the application
                must be in the system path on the remote system.

     -d         Don't wait for process to terminate (non-interactive).

     -e         Does not load the specified account's profile.

     -f         Copy the specified program even if the file already
                exists on the remote system.

     -i         Run the program so that it interacts with the desktop of the
                specified session on the specified system. If no session is
                specified the process runs in the console session.

     -h         [NOT IMPLEMENTED] If the target system is Vista or higher,
                has the process run with the account's elevated token, if
                available.

     -l         [EXPERIMENTAL] Run process as limited user (strips the
                Administrators group and allows only privileges assigned to
                the Users group). On Windows Vista the process runs with Low
                Integrity.

     -n         Specifies timeout in seconds connecting to remote computers.

     -p         Specifies optional password for user name. If you omit this
                you will be prompted to enter a hidden password.

     -s         Run the process in the System account.

     -u         Specifies optional user name for login to remote
                computer.

     -v         Copy the specified file only if it has a higher version number
                or is newer on than the one on the remote system.

     -w         Set the working directory of the process (relative to
                remote computer).

     -x         Display the UI on the Winlogon secure desktop (Local System
                only).

     -<priority> Specify -low, -belownormal, -abovenormal, -high or
                -realtime to run the process at a different priority. Use
                -background to run at low memory and I/O priority on Vista.

     computer   Direct PAExec to run the application on the remote
                computer or computers specified. If you omit the computer
                name PAExec runs the application on the local system,
                and if you specify a wildcard (\\*), PAExec runs the
                command on all computers in the current domain.

     @file      PAExec will execute the command on each of the computers
                listed in the file.

     program    Name of application to execute.

     arguments  Arguments to pass (note that file paths must be absolute
                paths on the target system).

Additional options only available in PAExec:

     -cnodel   If a file is copied to the server with -c, it is normally
               deleted (unless -d is specified).  -cnodel indicates the file
               should not be deleted.

     -csrc     When using -c (copy), -csrc allows you to specify an
               alternate path to copy the program from.
               Example: -c -csrc "C:\test path\file.exe"

     -dbg      Output to DebugView (OutputDebugString)

     -dfr      Disable WOW64 File Redirection for the new process

     -lo       Log Output to file.  Ex: -lo C:\Temp\PAExec.log
               The file will be UTF-8 with a Byte Order Mark at the start.

     -rlo      Remote Log Output: Log from remote service to file (on remote
               server).
               Ex: -rlo C:\Temp\PAExec.log
               The file will be UTF-8 with a Byte Order Mark at the start.

The application name, copy source, working directory and log file
entries can be quoted if the path contains a space.  For example:
PAExec \\test-server -w "C:\path with space" "C:\program files\app.exe"

Like PAExec, input is sent to the remote system when Enter is pressed,
and Ctrl-C stops the remote process and stops PAExec.

PsExec passes all parameters in clear-text.  In contrast, PAExec will scramble
the parameters to protect them from casual wire sniffers, but they are NOT
encrypted.  Note that data passed between PAExec and the remote program is NOT
scrambled or encrypted -- the same as with PsExec.

PAExec will return the error code it receives from the application that was
launched remotely.  If PAExec itself has an error, the return code will be
one of:

   -1 = internal error
   -2 = command line error
   -3 = failed to launch app (locally)
   -4 = failed to copy PAExec to remote (connection to ADMIN$ might have
        failed)
   -5 = connection to server taking too long (timeout)
   -6 = PAExec service could not be installed/started on remote server
   -7 = could not communicate with remote PAExec service
   -8 = failed to copy app to remote server