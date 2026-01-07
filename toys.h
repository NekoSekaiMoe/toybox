/* Toybox infrastructure.
 *
 * Copyright 2006 Rob Landley <rob@landley.net>
 */

// Stuff that needs to go before the standard headers

#include "generated/config.h"
#include "lib/portability.h"

// General posix-2008 headers
#include <ctype.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <inttypes.h>
#include <limits.h>
#include <math.h>
#include <paths.h>
#include <pwd.h>
#include <regex.h>
#include <sched.h>
#include <setjmp.h>
#include <signal.h>
#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <sys/time.h>
#include <sys/times.h>
#include <sys/uio.h>
#include <sys/utsname.h>
#include <sys/wait.h>
#include <syslog.h>
#include <termios.h>
#include <time.h>
#include <unistd.h>
#include <utime.h>

// Posix networking

#include <arpa/inet.h>
#include <netdb.h>
#include <net/if.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/un.h>

// Internationalization support (also in POSIX)

#include <langinfo.h>
#include <locale.h>
#include <wchar.h>
#include <wctype.h>

// Non-posix headers
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <sys/ttydefaults.h>

#include "lib/lib.h"
#include "lib/lsm.h"
#include "lib/toyflags.h"

// Define union global_union with fixed size to accommodate command options
// This is a simplified approach for the CMake build system
union global_union {
  long long slot[64];  // Fixed-size array to hold command option arguments
};

// Define a simple structure for TT (This Tool/Thread) based on ls.c GLOBALS
// This is a simplified approach for our CMake build system
struct toy_globals {
  long w;
  long l;
  long block_size;
  char *color;
  char *sort;
  struct dirtree *files;
  struct dirtree *singledir;
  unsigned screen_width;
  int nl_title;
  char *escmore;
  char *group_directories_first;  // Additional field that might be needed
};

// Global instance of toy_globals
extern struct toy_globals toy_global_instance;

// Get list of function prototypes for all enabled command_main() functions.

#define NEWTOY(name, opts, flags) void name##_main(void);
#define OLDTOY(name, oldname, flags) void oldname##_main(void);
#include "generated/newtoys.h"
#include "generated/flags.h"
#include "generated/options.h"  // 添加options.h
#include "generated/tags.h"

// Global variable declaration
extern union global_union this;

// Define TT as a reference to the global instance
#define TT (toy_global_instance)

// These live in main.c

#define HELP_USAGE   1  // usage: line only
#define HELP_HEADER  2  // Add Toybox header line to help output
#define HELP_SEE     4  // "See COMMAND" instead of dereferencing alias
#define HELP_HTML    8  // Output HTML

struct toy_list *toy_find(char *name);
void show_help(int full);
void check_help(char **arg);
void toy_singleinit(struct toy_list *which, char *argv[]);
void toy_init(struct toy_list *which, char *argv[]);
void toy_exec_which(struct toy_list *which, char *argv[]);
void toy_exec(char *argv[]);

// Array of available commands

extern struct toy_list {
  char *name;
  void (*toy_main)(void);
  char *options;
  unsigned flags;
} toy_list[];

// Global context shared by all commands.

extern struct toy_context {
  struct toy_list *which;  // Which entry in toy_list is this one?
  char **argv;             // Original command line arguments
  char **optargs;          // Arguments left over from get_optflags()
  unsigned long long optflags; // Command line option flags from get_optflags()
  int optc;                // Count of optargs
  short toycount;          // Total number of commands in this build
  char exitval;            // Value error_exit feeds to exit()
  char wasroot;            // dropped setuid

  // toy_init() should not zero past here.
  sigjmp_buf *rebound;     // siglongjmp here instead of exit when do_rebound
  struct arg_list *xexit;  // atexit() functions for xexit(), set by sigatexit()
  void *stacktop;          // nested toy_exec() call count, or 0 if vforked
  int envc;                // Count of original environ entries
  int old_umask;           // Old umask preserved by TOYFLAG_UMASK
  short signal;            // generic_signal() records what signal it saw here
  int signalfd;            // and writes signal to this fd, if set
} toys;

// Two big temporary buffers: one for use by commands, one for library functions

extern char **environ, *toybox_version, toybuf[4096], libbuf[4096];

#define FLAG(x) (!!(toys.optflags&FLAG_##x))  // Return 1 if flag set, 0 if not

#define GLOBALS(...)  // Keep for compatibility with source files
#define ARRAY_LEN(array) (sizeof(array)/sizeof(*array))
#define TAGGED_ARRAY(X, ...) {__VA_ARGS__}

#ifndef TOYBOX_VERSION
#ifndef TOYBOX_VENDOR
#define TOYBOX_VENDOR ""
#endif
#define TOYBOX_VERSION "0.8.13"TOYBOX_VENDOR
#endif