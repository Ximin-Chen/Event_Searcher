#!flask/bin/python
import os
import unittest

from config import basedir
from app import app, db
from app.models import User,Post,Event

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
        self.app = app.test_client()

        db.session.commit()
        db.drop_all()
        db.create_all()

        admin = User(username="admin", password_hash="admin2016",first_name="admin",last_name="admin2", email="admin@gmail.com")
        post1=  Post(id="1", body="test", user_id="admin")
        event1 = Event(name="Test", id="1")
        db.session.add(admin)
        db.session.add(post1)
        db.session.add(event1)
        db.session.commit()




    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_home_status_code(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/') 

        # assert the status code of the response
        self.assertEqual(result.status_code, 200) 



class TestModels(TestCase):

    def test_User_model(self):
        """
        Test number of records in Employee table
        """
        self.assertEqual(User.query.count(), 1)

    def test_Post_model(self):
        """
        Test number of records in Employee table
        """
        self.assertEqual(Post.query.count(), 1)       

    def test_Event_model(self):
        """
        Test number of records in Employee table
        """
        self.assertEqual(Event.query.count(), 1)

def register(self, user_id, password, first_name,last_name):
    return self.app.post(
        '/register',
        data=dict(username=user_id, first_name= first_name, last_name=last_name,password=password ),
        follow_redirects=True
    )
 
def login(self, username, password):
    return self.app.post(
        '/login',
        data=dict(username=username, password=password),
        follow_redirects=True
    )

def test_valid_user_registration(self):
    response = self.register('patkennedy79@gmail.com', 'FlaskIsAwesome', 'FlaskIsAwesome')
    self.assertEqual(response.status_code, 200)
    self.assertIn(b'Thanks for registering!', response.data)  
   


if __name__ == '__main__':
    unittest.main()