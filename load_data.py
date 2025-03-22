from db import Database


def main():
    database = Database("asn.db")
    database.create_tables("scripts/asn_up.sql")

    with open("data/ip2asn-v4-u32.tsv", "r") as f:
        for line in f.read().splitlines():
            parts = line.split("\t")
            start, end, asn, country, registered = parts
            database.insert_asn_record(int(asn), start, end, country, registered)

        database.commit()


if __name__ == '__main__':
    main()
