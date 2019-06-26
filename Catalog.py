# !/usr/bin/env python3
from flask import (
    Flask,
    flash,
    jsonify,
    request,
    redirect,
    render_template,
    url_for
)

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import create_engine
from flask import make_response
from flask import session as login_session
import sys
import os
import random
import string
import httplib2
import json
import requests
app = Flask(__name__)

Base = declarative_base()
# creation of admin db


class Admin(Base):
    __tablename__ = "admin"
    admin_id = Column(Integer, primary_key=True)
    admin_mail = Column(String(100), nullable=False)


# db for chairs
class Chair(Base):
    __tablename__ = "chair"
    chair_id = Column(Integer, primary_key=True)
    chair_name = Column(String(100), nullable=False)
    chair_admin = Column(Integer, ForeignKey('admin.admin_id'))
    chair_relation = relationship(Admin)

    @property
    def details(self):
        return {
                'id': self.chair_id,
                'name': self.chair_name

        }


# databse for items
class Items(Base):
    __tablename__ = "items"
    item_id = Column(Integer, primary_key=True)
    item_name = Column(String(100), nullable=False)
    item_price = Column(Integer, nullable=False)
    item_weight = Column(Integer, nullable=False)
    item_brand = Column(String(100), nullable=False)
    item_image = Column(String(1000), nullable=False)
    chair_id = Column(Integer, ForeignKey('chair.chair_id'))
    item_relation = relationship(
        Chair,
        backref=backref("items", cascade="all,delete"))

    @property
    def details(self):
        return {
                'name': self.item_name,
                'price': self.item_price,
                'weight': self.item_weight,
                'brand': self.item_brand,
                'img_url': self.item_image

        }
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())
CLIENT_ID = CLIENT_ID['web']['client_id']
# to connect to database engine
engine = create_engine('sqlite:///chairs.db')
Base.metadata.create_all(engine)
# to create session

session = scoped_session(sessionmaker(bind=engine))


# This method is for home page
@app.route('/')
@app.route('/homeretrieve')
def homeretrieve():
    i = session.query(Items).all()
    return render_template('ShowItems.html', Items=i)


# This method is to show categories
@app.route('/chairs/categorylist', methods=['GET'])
def showcat():
    if request.method == 'GET':
        cat_list = session.query(Chair).all()
        return render_template('ShowCategory.html', categories=cat_list)


# This method is to show data in json
@app.route('/chairs/all.json')
def chair():
    chair = session.query(Items).all()
    return jsonify(Items=[i.details for i in chair])


# This method is to show each category in json
@app.route('/chairs/category/<int:id>/items.json')
def itemjson(id):
    chair = session.query(Items).filter_by(chair_id=id).all()
    return jsonify(Items=[i.details for i in chair])


@app.route('/chairs/category/json')
def categoryjson():
    catchair = session.query(Chair).all()
    return jsonify(Categories=[c.details for c in catchair])


@app.route('/read')
def readdata():
    chair = session.query(Items).all()
    msg = ""
    for i in chair:
        msg += str(i.item_name)
    return msg


# This method is to edit the category
@app.route('/chairs/category/<int:category_id>/edit', methods=['GET', 'POST'])
def catedit(category_id):
    if not login_session.get('email', None):
        flash('you should login')
        return redirect(url_for('homeretrieve'))
    admin = session.query(Admin).filter_by(
        admin_mail=login_session['email']
        ).one_or_none()
    chair = session.query(Chair).filter_by(chair_id=category_id).one_or_none()
    if not admin:
        return redirect(url_for('homeretrieve'))
    login_admin_id = admin.admin_id
    admin_id = chair.chair_admin
    if login_admin_id != admin_id:
        flash('ur not authencated so try later...........')
        return redirect(url_for('homeretrieve'))
    if not chair:
        flash('no category')
        return redirect(url_for('homeretrieve'))
    if request.method == 'GET':
        return render_template(
            'EditCategory.html',
            chair_name=chair.chair_name,
            id_category=category_id
            )
    else:
        cat_name = request.form['category_name']
        chair.chair_name = cat_name
        session.add(chair)
        session.commit()
        flash('updation done successfully')
        return redirect(url_for('homeretrieve'))


# This method is used to add a new category
@app.route('/chairs/category/new', methods=['GET', 'POST'])
def catnew():
    if not login_session.get('email', None):
        flash('you should login')
        return redirect(url_for('homeretrieve'))
    if request.method == 'POST':
        cat_name = request.form['category_name']
        if cat_name:
            admin = session.query(Admin).filter_by(
                admin_mail=login_session['email']
                ).one_or_none()
            if not admin:
                return redirect(url_for('homeretrieve'))
            admin_id = admin.admin_id
            new_chair = Chair(chair_name=cat_name, chair_admin=admin_id)
            session.add(new_chair)
            session.commit()
            flash('your chair added')
            return redirect(url_for('homeretrieve'))
        else:
            flash('retry........')
            return redirect(url_for('homeretrieve'))
    else:
        return render_template('NewCategory.html')
# This method is to delete category


@app.route('/chairs/category/<int:category_id>/delete')
def catdelete(category_id):
    if not login_session.get('email', None):
        flash('you should login')
        return redirect(url_for('homeretrieve'))
    admin = session.query(Admin).filter_by(
        admin_mail=login_session['email']
        ).one_or_none()
    chair = session.query(Chair).filter_by(chair_id=category_id).one_or_none()
    if not admin:
        return redirect(url_for('homeretrieve'))
    login_admin_id = admin.admin_id
    admin_id = chair.chair_admin
    if login_admin_id != admin_id:
        flash('ur not authencated so try later...........')
        return redirect(url_for('homeretrieve'))
    if not chair:
        flash('no category')
        return redirect(url_for('homeretrieve'))
    n = chair.chair_name
    session.delete(chair)
    session.commit()
    flash(' Category successfully deleted '+str(n))
    return redirect(url_for('homeretrieve'))
# This method is to update item


@app.route(
    '/chairs/category/<int:categoryid>/items/<int:itemid>/edit',
    methods=['GET', 'POST']
    )
def itemupdate(categoryid, itemid):
    if not login_session.get('email', None):
        flash('you should login')
        return redirect(url_for('homeretrieve'))
    admin = session.query(Admin).filter_by(
        admin_mail=login_session['email']
        ).one_or_none()
    if not admin:
        return redirect(url_for('homeretrieve'))
    itname = session.query(Items).filter_by(
        chair_id=categoryid, item_id=itemid
        ).one_or_none()
    catname = session.query(Chair).filter_by(chair_id=categoryid).one_or_none()
    login_admin_id = admin.admin_id
    admin_id = catname.chair_admin
    if catname is None:
        flash('category unavailable')
        return redirect(url_for('homeretrieve'))

    if not itname:
        flash('invalid item')
        return redirect(url_for('homeretrieve'))

    if login_admin_id != admin_id:
        flash('Not correct person to edit this particular item')
        return redirect(url_for('homeretrieve'))
    if request.method == 'GET':
        itemedit = session.query(Items).filter_by(item_id=itemid).one_or_none()
        if itemedit:
            return render_template(
                'EditItem.html', chairname=itemedit.item_name,
                chairprice=itemedit.item_price,
                chairweight=itemedit.item_weight,
                chairbrand=itemedit.item_brand,
                chairimage=itemedit.item_image,
                catid=categoryid, iid=itemid
                )
        else:
            flash('No elements Found Here')
            return redirect(url_for('homeretrieve'))

    else:
        name = request.form['chairname']
        image = request.form['chairimage']
        price = request.form['chairprice']
        weight = request.form['chairweight']
        brand = request.form['chairbrand']
        i = session.query(Items).filter_by(
            chair_id=categoryid, item_id=itemid
            ).one_or_none()
        if i:
            i.item_name = name
            i.item_image = image
            i.item_price = price
            i.item_weight = weight
            i.item_brand = brand
        else:
            flash(' There were no items')
            return redirect(url_for('homeretrieve'))
        session.add(i)
        session.commit()
        flash('updation done successfully')
        return redirect(url_for('homeretrieve'))


@app.route('/chairs/category/<int:category_id>/items')
def showcatitems(category_id):
    if request.method == 'GET':
        i = session.query(Items).filter_by(chair_id=category_id)
    return render_template('ShowItems.html', Items=i)


# This method is to add new item in particular category
@app.route(
    '/chairs/category/<int:categoryid>/items/new',
    methods=['GET', 'POST']
    )
def additemnew(categoryid):
    if not login_session.get('email', None):
        flash('you should login first')
        return redirect(url_for('homeretrieve'))
    admin = session.query(Admin).filter_by(
        admin_mail=login_session['email']
        ).one_or_none()
    if not admin:
        return redirect(url_for('homeretrieve'))
    catname = session.query(Chair).filter_by(chair_id=categoryid).one_or_none()
    login_admin_id = admin.admin_id
    admin_id = catname.chair_admin
    if login_admin_id != admin_id:
        flash('ur not correct person to add')
        return redirect(url_for('homeretrieve'))
    if catname is None:
        flash('category unavailable')
        return redirect(url_for('homeretrieve'))
    if request.method == 'GET':
        return render_template('AddItem.html', cat_id=categoryid)
    else:
        name = request.form['chairname']
        image = request.form['chairimage']
        price = request.form['chairprice']
        weight = request.form['chairweight']
        brand = request.form['chairbrand']
        sid = categoryid
        cat_new = Items(
            item_name=name, item_price=price,
            item_weight=weight, item_brand=brand,
            item_image=image, chair_id=sid
            )
        session.add(cat_new)
        session.commit()
        flash('Item added Sucessfully')
        return redirect(url_for('homeretrieve'))
# This method is used to remove item


@app.route('/chairs/category/<int:categoryid>/items/<int:itemid>/delete')
def removeitem(categoryid, itemid):
    if not login_session.get('email', None):
        flash('you should login')
        return redirect(url_for('homeretrieve'))
    admin = session.query(Admin).filter_by(
        admin_mail=login_session['email']
        ).one_or_none()
    if not admin:
        return redirect(url_for('homeretrieve'))
    catname = session.query(Chair).filter_by(chair_id=categoryid).one_or_none()
    login_admin_id = admin.admin_id
    admin_id = catname.chair_admin
    itname = session.query(Items).filter_by(
        chair_id=categoryid, item_id=itemid
        ).one_or_none()
    if catname is None:
        flash('category unavailable')
        return redirect(url_for('homeretrieve'))

    if not itname:
        flash('invalid item')
        return redirect(url_for('homeretrieve'))

    if login_admin_id != admin_id:
        flash('ur not correct person to edit')
        return redirect(url_for('homeretrieve'))
    item = session.query(Items).filter_by(item_id=itemid).one_or_none()
    if item:
        name = item.item_name
        session.delete(item)
        session.commit()
        flash('deleted successfully '+str(name))
        return redirect(url_for('homeretrieve'))
    else:
        flash('item not found')
        return redirect(url_for('homeretrieve'))


@app.route('/chairs/recentitems')
def recentitems():
    if request.method == 'GET':
        cat_list = session.query(Items).all()
    return render_template('Recentitems.html', categories=cat_list)

# showing details of particular item


@app.route(
    '/chairs/category/<int:category_id>/items/<int:itemid>',
    methods=['GET', 'POST']
    )
def iteminfo(category_id, itemid):
    if request.method == 'GET':
        i = session.query(Items).filter_by(
            chair_id=category_id, item_id=itemid
            ).one_or_none()
        return render_template(
            'ItemDetails.html',
            infoname=i.item_name,
            infoprice=i.item_price, infoweight=i.item_weight,
            infobrand=i.item_brand, infomage=i.item_image
        )

# This method is for login


@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('NewLogin.html', STATE=state)


""" GConnection """


@app.route('/gconnect', methods=['POST', 'GET'])
def gConnect():
    if request.args.get('state') != login_session['state']:
        response.make_response(json.dumps('Invalid State paramenter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    request.get_data()
    code = request.data.decode('utf-8')
    try:
        """ credentials """
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps("""Failed to upgrade the authorisation code"""), 401
            )
        response.headers['Content-Type'] = 'application/json'
        return response
# Checking access token

    access_token = credentials.access_token
    myurl = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    header = httplib2.Http()
    result = json.loads(header.request(myurl, 'GET')[1].decode('utf-8'))

    """ Error occur means then abort. """

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    """ Verifying. """

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
                            """Token's user ID does not
                            match given user ID."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    """ Verifying access token valid. """

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            """Token's client ID
            does not match app's."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    """ Storing access token. """

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Currently the user is already connected.'), 200
            )
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    """ info """

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    """ Login session """
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    admin_id = userID(login_session['email'])
    if not admin_id:
        admin_id = createNewUser(login_session)
    login_session['owner_id'] = admin_id
    flash("welcome...... you are in  %s" % login_session['email'])
    return 'you are logged in .... Welcome'


def createNewUser(login_session):
    email = login_session['email']
    newAdmin = Admin(admin_mail=email)
    session.add(newAdmin)
    session.commit()
    admin = session.query(Admin).filter_by(admin_mail=email).first()
    adminId = admin.admin_id
    return adminId


def userID(admin_mail):
    try:
        owner = session.query(Admin).filter_by(admin_mail=admin_mail).one()
        return owner.admin_id
    except Exception as e:
        print(e)
        return None
""" Gdisconnect """


@app.route('/gdisconnect')
def gdisconnect():
    """ Disconnected user. """
    del login_session['email']
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('The current user was disconnected.'), 401
            )
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    header = httplib2.Http()
    result = header.request(url, 'GET')[0]

    if result['status'] == '200':

        """ Reset process """

        del login_session['access_token']
        del login_session['gplus_id']
        response = redirect(url_for('homeretrieve'))
        response.headers['Content-Type'] = 'application/json'
        flash("Signed out", "success")
        return response
    else:

        """ unable to revoke token """
        response = make_response(json.dumps('Revoke token was failed'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/logout')
def logout():
    if login_session.get('email', None):
        return gdisconnect()
    return redirect(url_for('homeretrieve'))


@app.context_processor
def inject_all():
    chai = session.query(Chair).all()
    return dict(mychai=chai)


if __name__ == '__main__':
    app.secret_key = "chair@123"
    app.run(debug=True, host="localhost", port=5000)
