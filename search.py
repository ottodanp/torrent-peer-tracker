from db import Database

COMMANDS = {
    "peer count": ("Peer Count", "SELECT COUNT(*) FROM PEERS"),
    "torrent count": ("Torrent Count", "SELECT COUNT(*) FROM TORRENTS"),
    "peer transfer count": ("Peer Transfer Count", "SELECT COUNT(*) FROM TRANSFERS"),
    "peers uploaded to": ("Peers uploaded to", "SELECT COUNT(*) FROM TRANSFERS WHERE PEER_UPLOADED > 0"),
    "peers downloaded from": ("Peers Downloaded from", "SELECT COUNT(*) FROM TRANSFERS WHERE PEER_DOWNLOADED > 0"),
    "total uploaded": ("Total Uploaded", "SELECT SUM(PEER_UPLOADED) FROM TRANSFERS"),
    "total downloaded": ("Total downloaded", "SELECT SUM(PEER_DOWNLOADED) FROM TRANSFERS"),
    "peers": ("Peers", "SELECT * FROM PEERS"),
    "torrents": ("Torrents", "SELECT * FROM TORRENTS"),
    "transfers": ("Transfers", "SELECT * FROM TRANSFERS"),
    "peer transfers": ("Peer Transfers", "SELECT * FROM transfers WHERE PEER_UPLOADED > 0 OR PEER_DOWNLOADED > 0 "),
}


def command_ui_loop(database: Database):
    while True:
        for i, command in enumerate(COMMANDS):
            print(f"{i + 1}: {command}")

        entry = input("database> ")
        if entry == "exit":
            break

        if entry.isdigit():
            entry = int(entry) - 1
            if entry < 0 or entry >= len(COMMANDS):
                print("Invalid command")
                return
            command = list(COMMANDS.keys())[entry]
        else:
            command = entry.lower()

        database.execute(COMMANDS[command][1])
        data = database.fetchall()
        if data:
            print(data)


def raw_sql_loop(database: Database):
    while (i := input("database> ")) != "exit":
        database.execute(i)
        data = database.fetchall()
        if data:
            print(data)


def main():
    database = Database("tracker.db")
    commit = input("Commit changes? (y/n) ").lower() == "y"

    i = input("1: Preset Commands\n2: Raw SQL\n> ")
    command_ui_loop(database) if i == "1" else raw_sql_loop(database)

    if commit:
        database.commit()

    database.close()


if __name__ == "__main__":
    main()
