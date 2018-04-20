import unittest
from fp import *

class TestDatabase(unittest.TestCase):

    def test_create_database(self):
        conn = sqlite3.connect("broadwayshows.db")
        cur = conn.cursor()

        set_up_database()

        title_list = get_show_lst("broadway")
        sql = 'SELECT Title, Duration FROM Shows'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertTrue(len(result_list) == 0)

        conn.close()

    def test_get_shows(self):
        conn = sqlite3.connect("broadwayshows.db")
        cur = conn.cursor()

        set_up_database()
        get_shows("Wicked")
        sql = 'SELECT COUNT(*) FROM Shows'
        results = cur.execute(sql)
        result_list = results.fetchone()[0]
        self.assertTrue(result_list == 1)

        sql = "SELECT COUNT(*) FROM Shows WHERE Title = 'Wicked'"
        results = cur.execute(sql)
        result_list = results.fetchone()[0]
        self.assertTrue(result_list == 1)

        sql = "SELECT PreviewDate FROM Shows WHERE Title = 'Wicked'"
        results = cur.execute(sql)
        result_list = results.fetchone()[0]
        self.assertEqual(result_list, "Oct 08, 2003")

        sql = "SELECT Duration FROM Shows WHERE Title = 'Wicked'"
        results = cur.execute(sql)
        result_list = results.fetchone()[0]
        self.assertEqual(result_list, "2hrs, 45mins")

        conn.close()


    def test_ShowTimes_table(self):
        conn = sqlite3.connect("broadwayshows.db")
        cur = conn.cursor()

        set_up_database()

        title_list = get_show_lst("broadway")
        sql = 'SELECT * FROM ShowTimes'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertTrue(len(result_list) == 0)

        conn.close()

    def test_get_showtimes(self):
        conn = sqlite3.connect("broadwayshows.db")
        cur = conn.cursor()

        set_up_database()
        get_shows("Wicked")
        sql = 'SELECT COUNT(*) FROM ShowTimes'
        results = cur.execute(sql)
        result_list = results.fetchone()[0]
        self.assertFalse(result_list == 1)

        sql = "SELECT TitleId FROM ShowTimes"
        results = cur.execute(sql)
        result_list = results.fetchone()[0]
        self.assertTrue(result_list == 1)


        conn.close()

    def test_joins(self):
        conn = sqlite3.connect("broadwayshows.db")
        cur = conn.cursor()

        set_up_database()
        get_shows("Wicked")
        sql = 'SELECT Title, ShowTimes.TitleId FROM Shows JOIN ShowTimes ON Shows.Id = ShowTimes.TitleId'
        results = cur.execute(sql)
        result_list = results.fetchone()
        self.assertEqual(result_list[1], 1)
        self.assertEqual(result_list[0], "Wicked")

        conn.close()


class TestDataCollection(unittest.TestCase):

    def test_shows_data(self):
        conn = sqlite3.connect("broadwayshows.db")
        cur = conn.cursor()

        set_up_database()
        c = get_show_lst("broadway")
        x = get_shows("The Lion King", c)
        self.assertEqual(type(x), tuple)
        self.assertEqual(len(x), 3)
        self.assertEqual(type(x[0]), str)

        conn.close()

class TestDataProcessing(unittest.TestCase):

    def test_Shows_table(self):

        conn = sqlite3.connect("broadwayshows.db")
        cur = conn.cursor()

        set_up_database()
        get_shows("Wicked")
        sql = "SELECT [Time] FROM ShowTimes WHERE TitleId = 1"
        results = cur.execute(sql)
        result_list = results.fetchone()[0]
        self.assertEqual(result_list, "8:00PM")

        sql = "SELECT WeekDay FROM ShowTimes WHERE TitleId = 1"
        results = cur.execute(sql)
        result_list = results.fetchone()[0]
        self.assertEqual(result_list, "Fri")

        conn.close()



unittest.main()
