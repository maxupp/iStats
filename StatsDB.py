import pandas as pd
import sqlite3 as sl
from IScraper import IScraper


class StatsDB:
    def __init__(self, db_path):
        self.scraper = IScraper()
        try:
            self.con = sl.connect(db_path)
            self.con.row_factory = sl.Row
            self.cursor = self.con.cursor()
            self.initialize()
        except Exception as e:
            print(e)
            raise

    def initialize(self):
        with self.con:
            self.con.execute("""
                CREATE TABLE IF NOT EXISTS driver(
                    discord_id text,
                    iracing_display_name text,
                    iracing_cust_id integer
                )            
            """)

            self.con.execute("""
                CREATE TABLE IF NOT EXISTS team(
                    team_id integer PRIMARY KEY AUTOINCREMENT,
                    team_name text
                )            
            """)

            self.con.execute("""
                CREATE TABLE IF NOT EXISTS many_driver_has_many_team(
                    iracing_cust_id integer,
                    team_id integer,
                    FOREIGN KEY(iracing_cust_id) REFERENCES driver(iracing_cust_id),
                    FOREIGN KEY(team_id) REFERENCES team(team_id)
                )            
            """)

    def add_driver(self, iracing_display_name, discord_id):
        sql = "INSERT INTO driver (discord_id, iracing_display_name) values(?, ?)"
        data = [
            (discord_id, iracing_display_name)
        ]
        with self.con:
            self.con.executemany(sql, data)

    def lookup_driver(self, discord_id):
        result = self.con.execute(f'select iracing_display_name from driver where discord_id={discord_id}')
        return [x[0] for x in result]

    def sql(self, sql):
        return self.con.execute(sql)
