import mysql.connector
from datetime import datetime


class MySQLClient:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self._connection = None

    def connect(self):
        self._connection = mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def disconnect(self):
        if self._connection:
            self._connection.close()
            self._connection = None

    def save_candidate(
        self,
        sender_email,
        sender_name,
        subject,
        received_at,
        filename,
        file_type,
        classification,
        extracted_text,
        char_count
    ):
        query = """
        INSERT INTO candidates
        (sender_email, sender_name, subject, received_at,
         filename, file_type, classification,
         extracted_text, char_count, processed_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        cursor = self._connection.cursor()
        cursor.execute(
            query,
            (
                sender_email,
                sender_name,
                subject,
                received_at,
                filename,
                file_type,
                classification,
                extracted_text,
                char_count,
                datetime.now()
            )
        )
        self._connection.commit()
        cursor.close()
