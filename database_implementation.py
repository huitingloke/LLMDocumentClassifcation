import sqlite3
import os

# Connect to SQLite database (it will create a new one if it doesn't exist)
conn = sqlite3.connect('file_storage.db')
conn.execute('''CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            filename TEXT,
            filedata BLOB
        );''')
conn.commit()

def store_file(conn, file_id, file_path):
    """Store the file into the database with a custom file_id."""
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()

        filename = os.path.basename(file_path)
        # Insert file into the database with a user-specified file_id
        try:
            conn.execute('''INSERT INTO files (id, filename, filedata) VALUES (?, ?, ?);''', 
                         (file_id, filename, file_data))
            conn.commit()
            print(f"File '{filename}' stored successfully with ID {file_id}.")
            return True
        except sqlite3.IntegrityError:
            print(f"Error: The file ID {file_id} already exists. Please choose a different ID.")

    except Exception as e:
        print(f"An error occurred: {e}")

def retrieve_file(conn, file_id, output_path):
    """Retrieve a file from the database by the chosen file_id."""
    cursor = conn.cursor()
    cursor.execute('''SELECT filename, filedata FROM files WHERE id = ?;''', (file_id,))
    file = cursor.fetchone()

    if file:
        filename, file_data = file
        with open(output_path, 'wb') as output_file:
            output_file.write(file_data)
        print(f"File '{filename}' retrieved successfully to {output_path}.")
    else:
        print(f"No file found with ID {file_id}.")
def delete_file(file_id, conn=conn):
    """Delete a file from the database."""
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM files WHERE id = ?;''', (file_id,))
    conn.commit()
    print(f"File with ID {file_id} deleted successfully.")

def list_files(conn=conn):
    """List all stored files in the database."""
    cursor = conn.cursor()
    cursor.execute('''SELECT id, filename FROM files;''')
    files = cursor.fetchall()
    
    if files:
        print("Stored files:")
        for file in files:
            print(f"ID: {file[0]}, Filename: {file[1]}")
    else:
        print("No files stored in the database.")