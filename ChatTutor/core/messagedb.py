import pymysql
import uuid
import datetime


class MessageSchema:
    mes_id = ""
    role = ""
    content = ""
    chat_key = ""
    clear_number = 0
    time_created = ""

    def convert_to_dictionary(self):
        return {
            "mes_id": self.mes_id,
            "role": self.role,
            "content": self.content,
            "chat_key": self.chat_key,
            "clear_number": self.clear_number,
            "time_created": self.clear_number,
        }


class ChatSchema:
    chat_id = ""

    def convert_to_dictionary(self):
        return {"chat_id": self.chat_id}


class MessageDB:
    host = ""
    user = ""
    password = ""
    db = ""
    statisticsdb = ""

    # Only for deleting the db when you first access the site. Can be used for debugging
    presetTables1 = """
        DROP TABLE IF EXISTS lchats
    """
    # only for deleting the db when you first access the site. Can be used for debugging
    presetTables2 = """
        DROP TABLE IF EXISTS lmessages
    """

    chats_table_Sql = """
    CREATE TABLE IF NOT EXISTS lchats (
        chat_id varchar(100) PRIMARY KEY
        )"""

    messages_table_Sql = """
    CREATE TABLE IF NOT EXISTS lmessages (
        mes_id varchar(100) PRIMARY KEY,
        role text NOT NULL,
        content text NOT NULL,
        chat_key varchar(100) NOT NULL,
        clear_number integer NOT NULL,
        time_created text NOT NULL,
        FOREIGN KEY (chat_key) REFERENCES lchats (chat_id)
        )"""

    def __init__(self, host, user, password, database, statistics_database):
        self.host = host
        self.user = user
        self.password = password
        self.db = database
        self.statisticsdb = statistics_database

    def connect_to_messages_database(self):
        """Function that connects to the database"""
        connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            db=self.db,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

        return connection

    def connect_to_statistics_database(self):
        connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            db=self.statisticsdb,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

        return connection

    def initialize_ldatabase(self):
        """Creates the tables if they don't exist"""
        con = self.connect_to_messages_database()
        cur = con.cursor()
        # if you want to delete the database when a user acceses the site. (For DEBUGGING purposes only
        # cur.execute(presetTables1)
        # cur.execute(presetTables2)
        cur.execute(self.chats_table_Sql)
        cur.execute(self.messages_table_Sql)

    def insert_message(self, a_message):
        """This inserts a message into the sqlite3 database. the message must be sent as a dictionary"""
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
            role = a_message["role"]
            content = a_message["content"]
            chat_key = a_message["chat"]
            clear_number = a_message["clear_number"]
            time_created = a_message["time_created"]
            insert_format_lmessages = f"INSERT INTO lmessages (mes_id ,role, content, chat_key, clear_number, time_created) VALUES ('{uuid.uuid4()}','{role}', %s, '{chat_key}', {clear_number}, '{time_created}')"
            cur.execute(insert_format_lmessages, (content,))
            con.commit()

    def insert_chat(self, chat_key):
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
            insert_format_lchats = ""
            cur.execute(f"INSERT IGNORE INTO lchats (chat_id) VALUES ('{chat_key}')")
            con.commit()

    def execute_sql(self, sqlexec, commit=True):
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
            response = cur.execute(sqlexec)
            messages_arr = cur.fetchall()
            if commit:
                con.commit()
            return messages_arr

    def parse_messages(self, messages_arr):
        renderedString = (
            '<table class="messages-table"> <tr style="background-color: rgb(140, 0, 255); color: white"> '
            "<th> Role </th>"
            "<th> Content </th>"
            "<th> Number of clears </th>"
            "<th> Time </th>"
            "<th> Chat id </th>"
            " </tr>"
        )
        i = 0
        for message in messages_arr:
            role = message["role"]
            content = message["content"]
            chat_id = message["chat_key"]
            clear_number = message["clear_number"]
            time_cr = message["time_created"]
            style = "font-size: 10px; background-color: var(--msg-input-bg); overflow: hidden; padding: 2px; border-radius: 2px"
            side = "left"
            if role != "assistant":
                side = "right"

            chat_header = ""

            if i != 0:
                current_message = messages_arr[i]
                prev_message = messages_arr[i - 1]
                if current_message["chat_key"] != prev_message["chat_key"]:
                    chat_header = f"""
                        Chat id: {chat_id}
                    """

                if current_message["clear_number"] != prev_message["clear_number"]:
                    chat_header = f"""
                        Cleared {clear_number} from id {chat_id}
                    """
            else:
                chat_header = f"""
                    Chat id: {chat_id}
                """

            styl_td = ""
            i = i + 1

            timstp = 1000

            tr_header = ""
            if chat_header != "":
                tr_header = f'<tr style="color: var(--left-msg-txt); background-color: rgba(140, 0, 255, 0.5)"><td colspan="5">{chat_header}</td></tr>'

            msg_html = f"""
                            
                            {tr_header}
                           <tr style="color: var(--left-msg-txt); {styl_td}">
                                <td style={styl_td}>{role}</td>
                                <td style={styl_td}>{content}</td>
                                <td style={styl_td}>{clear_number}</td>
                                <td style={styl_td}>{datetime.datetime.utcfromtimestamp(timstp / 1000)}</td>
                                <td style={styl_td}>{chat_id}</td>
                           </tr>
                       """
            renderedString += msg_html

        renderedString += "</table>"
        return renderedString
