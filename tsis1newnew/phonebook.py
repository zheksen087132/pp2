import csv
import json
import os
from datetime import date, datetime
from connect import get_connection
 
 
# ── utils ──────────────────────────────────────────────────────────────────
 
def serial(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(type(obj))
 
 
def show(rows):
    if not rows:
        print("  (empty)\n")
        return
    print(f"\n{'ID':<5} {'Name':<22} {'Email':<26} {'Birthday':<12} {'Group':<10} Phones")
    print("-" * 95)
    for r in rows:
        cid, fn, ln, email, bday, grp, phones = r
        name = f"{fn or ''} {ln or ''}".strip()
        print(f"{cid:<5} {name:<22} {(email or ''):<26} {str(bday or ''):<12} {(grp or ''):<10} {phones or ''}")
    print()
 
 
def ensure_group(cur, name):
    cur.execute("INSERT INTO groups(name) VALUES(%s) ON CONFLICT(name) DO NOTHING", (name,))
    cur.execute("SELECT id FROM groups WHERE name=%s", (name,))
    return cur.fetchone()[0]
 
 
# ── CRUD ───────────────────────────────────────────────────────────────────
 
def add_contact(conn):
    fn    = input("First name : ").strip()
    ln    = input("Last name  : ").strip() or None
    email = input("Email      : ").strip() or None
    bday  = input("Birthday (YYYY-MM-DD): ").strip() or None
    grp   = input("Group (Family/Work/Friend/Other): ").strip() or "Other"
 
    with conn.cursor() as cur:
        gid = ensure_group(cur, grp)
        cur.execute(
            "INSERT INTO contacts(first_name,last_name,email,birthday,group_id) VALUES(%s,%s,%s,%s,%s) RETURNING id",
            (fn, ln, email, bday, gid)
        )
        cid = cur.fetchone()[0]
        while True:
            phone = input("Phone (blank to stop): ").strip()
            if not phone:
                break
            ptype = input("Type (home/work/mobile) [mobile]: ").strip() or "mobile"
            cur.execute("INSERT INTO phones(contact_id,phone,type) VALUES(%s,%s,%s)", (cid, phone, ptype))
    conn.commit()
    print(f"Added: {fn} (id={cid})")
 
 
def delete_contact(conn):
    name = input("First name to delete: ").strip()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM contacts WHERE first_name ILIKE %s RETURNING id", (name,))
        n = len(cur.fetchall())
    conn.commit()
    print(f"Deleted {n} contact(s).")
 
 
def update_contact(conn):
    name = input("First name to update: ").strip()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM contacts WHERE first_name ILIKE %s LIMIT 1", (name,))
        row = cur.fetchone()
        if not row:
            print("Not found.")
            return
        cid = row[0]
        email = input("New email (blank=skip): ").strip()
        bday  = input("New birthday (blank=skip): ").strip()
        if email:
            cur.execute("UPDATE contacts SET email=%s WHERE id=%s", (email, cid))
        if bday:
            cur.execute("UPDATE contacts SET birthday=%s WHERE id=%s", (bday, cid))
    conn.commit()
    print("Updated.")
 
 
# ── Search / Filter ────────────────────────────────────────────────────────
 
def search_all(conn):
    q = input("Search query: ").strip()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", (q,))
        show(cur.fetchall())
 
 
def filter_group(conn):
    grp = input("Group name: ").strip()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, g.name,
                   STRING_AGG(p.phone||' ('||COALESCE(p.type,'?')||')', ', ')
            FROM contacts c
            LEFT JOIN groups g ON g.id=c.group_id
            LEFT JOIN phones p ON p.contact_id=c.id
            WHERE g.name ILIKE %s
            GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
        """, (f"%{grp}%",))
        show(cur.fetchall())
 
 
def search_email(conn):
    em = input("Email fragment: ").strip()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, g.name,
                   STRING_AGG(p.phone||' ('||COALESCE(p.type,'?')||')', ', ')
            FROM contacts c
            LEFT JOIN groups g ON g.id=c.group_id
            LEFT JOIN phones p ON p.contact_id=c.id
            WHERE c.email ILIKE %s
            GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
        """, (f"%{em}%",))
        show(cur.fetchall())
 
 
def sorted_list(conn):
    print("Sort: 1) name  2) birthday  3) date added")
    m = {"1": "first_name", "2": "birthday", "3": "created_at"}
    order = m.get(input("Choice [1]: ").strip(), "first_name")
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM get_contacts_page(1000, 0, %s)", (order,))
        show(cur.fetchall())
 
 
def paginate(conn):
    size, offset = 3, 0
    while True:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_page(%s,%s,'first_name')", (size, offset))
            rows = cur.fetchall()
        show(rows)
        print(f"  offset={offset} | n=next  p=prev  q=quit")
        cmd = input("> ").strip().lower()
        if cmd == "n":
            if len(rows) == size:
                offset += size
            else:
                print("Last page.")
        elif cmd == "p":
            offset = max(0, offset - size)
        elif cmd == "q":
            break
 
 
# ── Stored procedure calls ─────────────────────────────────────────────────
 
def call_add_phone(conn):
    name  = input("Contact first name: ").strip()
    phone = input("Phone: ").strip()
    ptype = input("Type (home/work/mobile) [mobile]: ").strip() or "mobile"
    with conn.cursor() as cur:
        cur.execute("CALL add_phone(%s,%s,%s)", (name, phone, ptype))
    conn.commit()
    print("Phone added.")
 
 
def call_move_group(conn):
    name = input("Contact first name: ").strip()
    grp  = input("Group name: ").strip()
    with conn.cursor() as cur:
        cur.execute("CALL move_to_group(%s,%s)", (name, grp))
    conn.commit()
    print("Moved.")
 
 
# ── Import / Export ────────────────────────────────────────────────────────
 
def export_json(conn):
    path = input("Export path [contacts.json]: ").strip() or "contacts.json"
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, c.created_at,
                   g.name AS group_name,
                   JSON_AGG(JSON_BUILD_OBJECT('phone', p.phone, 'type', p.type))
                       FILTER (WHERE p.id IS NOT NULL) AS phones
            FROM contacts c
            LEFT JOIN groups g ON g.id=c.group_id
            LEFT JOIN phones p ON p.contact_id=c.id
            GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, c.created_at, g.name
        """)
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, default=serial, ensure_ascii=False)
    print(f"Exported {len(rows)} contacts to {path}")
 
 
def import_json(conn):
    path = input("Import path [contacts.json]: ").strip() or "contacts.json"
    if not os.path.exists(path):
        print("File not found.")
        return
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    ins = skipped = overwritten = 0
    with conn.cursor() as cur:
        for c in data:
            fn = (c.get("first_name") or "").strip()
            if not fn:
                continue
            cur.execute("SELECT id FROM contacts WHERE first_name ILIKE %s LIMIT 1", (fn,))
            existing = cur.fetchone()
            if existing:
                ans = input(f"'{fn}' exists. [s]kip/[o]verwrite? ").strip().lower()
                if ans != "o":
                    skipped += 1
                    continue
                cur.execute("DELETE FROM contacts WHERE id=%s", (existing[0],))
                overwritten += 1
            gid = ensure_group(cur, c.get("group_name") or "Other")
            cur.execute(
                "INSERT INTO contacts(first_name,last_name,email,birthday,group_id) VALUES(%s,%s,%s,%s,%s) RETURNING id",
                (fn, c.get("last_name"), c.get("email"), c.get("birthday"), gid)
            )
            cid = cur.fetchone()[0]
            for ph in (c.get("phones") or []):
                if ph and ph.get("phone"):
                    cur.execute("INSERT INTO phones(contact_id,phone,type) VALUES(%s,%s,%s)",
                                (cid, ph["phone"], ph.get("type", "mobile")))
            ins += 1
    conn.commit()
    print(f"Imported: {ins} new, {overwritten} overwritten, {skipped} skipped.")
 
 
def import_csv(conn):
    path = input("CSV path [contacts.csv]: ").strip() or "contacts.csv"
    if not os.path.exists(path):
        print("File not found.")
        return
    ins = skipped = 0
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        with conn.cursor() as cur:
            for row in reader:
                fn = row.get("first_name", "").strip()
                if not fn:
                    continue
                cur.execute("SELECT id FROM contacts WHERE first_name ILIKE %s LIMIT 1", (fn,))
                if cur.fetchone():
                    skipped += 1
                    continue
                gid = ensure_group(cur, row.get("group", "Other").strip() or "Other")
                cur.execute(
                    "INSERT INTO contacts(first_name,last_name,email,birthday,group_id) VALUES(%s,%s,%s,%s,%s) RETURNING id",
                    (fn, row.get("last_name") or None, row.get("email") or None,
                     row.get("birthday") or None, gid)
                )
                cid = cur.fetchone()[0]
                phone = row.get("phone", "").strip()
                if phone:
                    cur.execute("INSERT INTO phones(contact_id,phone,type) VALUES(%s,%s,%s)",
                                (cid, phone, row.get("phone_type", "mobile") or "mobile"))
                ins += 1
    conn.commit()
    print(f"CSV: {ins} inserted, {skipped} skipped.")
 
 
# ── Menu ───────────────────────────────────────────────────────────────────
 
MENU = """
=== PhoneBook TSIS 1 ===
1.  Add contact
2.  Delete contact
3.  Update contact
4.  Search (name/email/phone)
5.  Filter by group
6.  Search by email
7.  Sorted list
8.  Paginated browse
9.  Add phone (procedure)
10. Move to group (procedure)
11. Export to JSON
12. Import from JSON
13. Import from CSV
0.  Exit
"""
 
ACTIONS = {
    "1": add_contact,    "2": delete_contact,  "3": update_contact,
    "4": search_all,     "5": filter_group,    "6": search_email,
    "7": sorted_list,    "8": paginate,
    "9": call_add_phone, "10": call_move_group,
    "11": export_json,   "12": import_json,    "13": import_csv,
}
 
 
def main():
    conn = get_connection()
    print("Connected.")
    try:
        while True:
            print(MENU)
            choice = input(">> ").strip()
            if choice == "0":
                break
            fn = ACTIONS.get(choice)
            if fn:
                try:
                    fn(conn)
                except Exception as e:
                    conn.rollback()
                    print(f"Error: {e}")
            else:
                print("Unknown option.")
    finally:
        conn.close()
 
 
if __name__ == "__main__":
    main()