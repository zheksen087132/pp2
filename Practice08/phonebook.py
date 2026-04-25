import csv
from connect import connect


def insert_from_csv(filename):
    names = []
    phones = []

    try:
        with open(filename, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 2:
                    print(f"Skipped invalid row: {row}")
                    continue

                names.append(row[0].strip())
                phones.append(row[1].strip())

        conn = connect()
        cur = conn.cursor()

        cur.execute("CALL bulk_insert_contacts(%s, %s)", (names, phones))
        conn.commit()

        print("Bulk insert completed successfully")

        cur.close()
        conn.close()

    except FileNotFoundError:
        print("CSV file not found")
    except Exception as e:
        print("Error:", e)


def insert_from_console():
    name = input("Enter name: ").strip()
    phone = input("Enter phone: ").strip()

    conn = connect()
    cur = conn.cursor()

    try:
        cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
        conn.commit()
        print("Contact added/updated successfully")
    except Exception as e:
        conn.rollback()
        print("Error:", e)

    cur.close()
    conn.close()


def search_contacts_menu():
    pattern = input("Enter search pattern: ").strip()

    conn = connect()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
        rows = cur.fetchall()

        if rows:
            print("\nSearch results:")
            for row in rows:
                print(f"Name: {row[0]}, Phone: {row[1]}")
        else:
            print("No contacts found")
    except Exception as e:
        print("Error:", e)

    cur.close()
    conn.close()


def pagination():
    try:
        limit = int(input("Enter limit: "))
        offset = int(input("Enter offset: "))
    except ValueError:
        print("Limit and offset must be integers")
        return

    conn = connect()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
        rows = cur.fetchall()

        if rows:
            print("\nPaginated results:")
            for row in rows:
                print(f"Name: {row[0]}, Phone: {row[1]}")
        else:
            print("No contacts found")
    except Exception as e:
        print("Error:", e)

    cur.close()
    conn.close()


def delete_contact_menu():
    value = input("Enter username or phone to delete: ").strip()

    conn = connect()
    cur = conn.cursor()

    try:
        cur.execute("CALL delete_contact(%s)", (value,))
        conn.commit()
        print("Contact deleted successfully")
    except Exception as e:
        conn.rollback()
        print("Error:", e)

    cur.close()
    conn.close()


def main():
    while True:
        print("\n--- PHONEBOOK ---")
        print("1. Insert from CSV")
        print("2. Add / Update contact")
        print("3. Search contacts")
        print("4. Pagination")
        print("5. Delete contact")
        print("0. Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            insert_from_csv("contacts.csv")
        elif choice == "2":
            insert_from_console()
        elif choice == "3":
            search_contacts_menu()
        elif choice == "4":
            pagination()
        elif choice == "5":
            delete_contact_menu()
        elif choice == "0":
            print("Goodbye")
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()