import ldmud, apsw, traceback, warnings

def _get_object(efunname):
    ob = ldmud.efuns.this_object()
    if not ob:
        raise RuntimeError("%s() without current object." % (efunname,))
    if not isinstance(ob, ldmud.Object):
        raise RuntimeError("%s() from lightweight object." % (efunname,))
    return ob

def _authorizer(operation, arg1, arg2, dbname, view):
    if operation != apsw.SQLITE_PRAGMA:
        return apsw.SQLITE_OK

    try:
        if ldmud.get_master().functions.privilege_violation("sqlite_pragma", ldmud.efuns.this_object(), arg1, arg2, 0):
            return apsw.SQLITE_OK
        return apsw.SQLITE_DENY
    except:
        traceback.print_exc()
        return apsw.SQLITE_DENY

def efun_sl_open(filename: str) -> int:
    """
    SYNOPSIS
            int sl_open(string filename)

    DESCRIPTION
            Opens the file <filename> for use as a SQLite database.
            If the file doesn't exists it will be created.
            Only one open file per object is allowed. On success this
            function returns 1, otherwise usually an error is thrown.

    SEE ALSO
            sl_exec(E), sl_insert_id(E), sl_close(E)
    """
    ob = _get_object("sl_open")
    if hasattr(ob, "sqlite_connection"):
        raise RuntimeError("The current object already has a database open.")

    conn = apsw.Connection(filename)
    conn.execute("PRAGMA synchronous = OFF")
    conn.authorizer = _authorizer

    ob.sqlite_busy = False
    ob.sqlite_connection = conn

    return 1

def efun_sl_close() -> None:
    """
    SYNOPSIS
            void sl_close()

    DESCRIPTION
            Closes the SQLite database that is associated with the
            current object.

    SEE ALSO
            sl_open(E), sl_exec(E), sl_insert_id(E)
    """
    ob = _get_object("sl_close")
    conn = getattr(ob, "sqlite_connection", None)
    if not conn:
        raise RuntimeError("The current object doesn't have database open.")
    if ob.sqlite_busy:
        raise RuntimeError("Reentrant call to the same database.")

    ob.sqlite_busy = True
    conn.close()
    del ob.sqlite_connection

def efun_sl_exec(statement: str, *args) -> ldmud.Array:
    """
    SYNOPSIS
            mixed * sl_exec(string statement, ...)

    DESCRIPTION
            Executes the SQL statement <statement> for the current
            SQLite database. The SQL statement may contain wildcards like
            '?' and '?nnn', where 'nnn' is an integer. These wildcards
            can be given as further parameters to sl_exec. With '?nnn'
            the number of a specific parameter can be given, the first
            parameter has number 1.

            If the statement returns data, sl_exec returns an array
            with each row (which is itself an array of columns) as.
            an element.

            Pragma statements raise a privilege_violation ("sqlite_pragma",
            ob, name, value). If the privilege is denied, an error is
            thrown.

    SEE ALSO
            sl_open(E), sl_insert_id(E), sl_close(E)
    """
    ob = _get_object("sl_exec")
    conn = getattr(ob, "sqlite_connection", None)
    if not conn:
        raise RuntimeError("The current object doesn't have a database open.")
    if ob.sqlite_busy:
        raise RuntimeError("Reentrant call to the same database.")

    result = []
    for row in conn.execute(statement, args):
        result.append(ldmud.Array(row))

    return ldmud.Array(result)

def efun_sl_insert_id() -> int:
    """
    SYNOPSIS
            int sl_insert_id()

    DESCRIPTION
            After inserting a line into a table with an AUTO_INCREMENT field,
            this efun can be used to return the (new) value of the AUTO_INCREMENT
            field.

    SEE ALSO
            sl_open(E), sl_exec(E), sl_close(E)
    """
    ob = _get_object("sl_insert_id")
    conn = getattr(ob, "sqlite_connection", None)
    if not conn:
        raise RuntimeError("The current object doesn't have a database open.")
    if ob.sqlite_busy:
        raise RuntimeError("Reentrant call to the same database.")

    return conn.last_insert_rowid()

def register():
    ldmud.register_efun("sl_open", efun_sl_open)
    ldmud.register_efun("sl_close", efun_sl_close)
    ldmud.register_efun("sl_exec", efun_sl_exec)
    ldmud.register_efun("sl_insert_id", efun_sl_insert_id)

class LDMudVFS(apsw.VFS):

    def __init__(self):
        super().__init__("ldmud", "", makedefault=True)

    def xFullPathname(self, name):
        this = ldmud.efuns.this_object()
        euid = ldmud.efuns.geteuid(this)
        res = ldmud.get_master().functions.valid_write(name, euid, "sl_open", this)

        if not res:
            raise apsw.AuthError()

        if isinstance(res, str):
            fname = res
        else:
            fname = name

        if not len(fname) or "/.." in fname or ' ' in fname:
            raise apsw.AuthError()

        if fname[0] == "/":
            fname = fname[1:]
            if not len(fname):
                fname = "."
            elif fname[0] == "/":
                raise apsw.AuthError()

        return super().xFullPathname(fname)

ldmud_vfs = None

def init_sqlite():
    global ldmud_vfs

    def log_handler(rc: int, message: str) -> None:
        ob = ldmud.efuns.this_object()
        if not ob or not isinstance(ob, ldmud.Object):
            ldmud.efuns.debug_message("SQLite: %s (rc=%d)\n" % (message, rc), 12)
        elif (rc & 0xff) == apsw.SQLITE_WARNING:
            warnings.warn("SQLite: %s" % (message,), RuntimeWarning)
        else:
            ldmud.efuns.debug_message("SQLite (%s): %s (rc=%d)\n" % (ob.name, message, rc), 12)

    apsw.config(apsw.SQLITE_CONFIG_LOG, log_handler)
    try:
        apsw.config(apsw.SQLITE_CONFIG_URI, 0)
    except TypeError:
        apsw.config(apsw.SQLITE_CONFIG_URI)

    ldmud_vfs = LDMudVFS()

init_sqlite()
