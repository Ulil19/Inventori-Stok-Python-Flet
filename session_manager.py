# Kamus sesi global
session = {}


def set_session(user):
    """Menetapkan sesi pengguna."""
    session["user"] = user


def get_session():
    """Mengambil sesi pengguna saat ini."""
    return session.get("user")


def clear_session():
    """Menghapus sesi."""
    session.clear()
