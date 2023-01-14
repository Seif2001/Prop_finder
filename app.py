from flask import Flask, render_template, url_for, request, session
import pymysql as sql
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
#<table>
#  <tr>
#    {%for header in headings%}
#    <th>{{header}}</th>
#    {%endfor%}
#  </tr>
#
#  {%for row in data%} {%for cell in row%}
#  <tr>
#    <td>{{cell}}</td>
#    {%endfor%}
#  </tr>
#  {%endfor%}
#</table>


#,'title','prop_type', 'Bedrooms', 'Bathrooms', 'SizeSQM', 'SizeSQFT', 'Price', 'ListingDate', 'Discription', 'area', 'Location', "Developer", 'Agent_number', 'dev_project_nam')
mydb = sql.connect(
        host="db4free.net",
        port = 3306,
        user="seifelsayed",
        password="Seif_2001",
        database="p_finder"
)


mycursor = mydb.cursor()
sqls = """
select distinct area from property;
"""


mycursor.execute(sqls)
DistinctAreas = mycursor.fetchall()

print("hi")

sql2 = """
select phone_number from agent;
"""
mycursor = mydb.cursor()


mycursor.execute(sql2)
aPhoneNumbers = mycursor.fetchall()

sql7 = """
select distinct location from property;
"""
mycursor = mydb.cursor()

mycursor.execute(sql7)
cities = mycursor.fetchall()


sql9 = """
select distinct proj_name from development_project;
"""

mycursor = mydb.cursor()

mycursor.execute(sql9)
projs = mycursor.fetchall()

sql11 = """
select distinct amenity from amenities;
"""

mycursor = mydb.cursor()

mycursor.execute(sql11)
ammens = mycursor.fetchall()

sql14 = """
select distinct prop_type from property;
"""

mycursor = mydb.cursor()

mycursor.execute(sql14)
types = mycursor.fetchall()

@app.route('/' , methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        return render_template("index.html",  list = DistinctAreas, message = "")
    #headings = ['id']
    return render_template("index.html",  list = DistinctAreas, message = "")

global user1
@app.route('/login', methods = ['POST', 'GET'])
def InsertUser():
    if request.method == 'POST':
        user1 =  request.form["name"]
        session['user1'] = user1
        age = request.form["age"]
        birthdate = request.form["birthdate"]
        gender = request.form["gender"]
        Area1 = request.form["Area 1"]
        Area2 = request.form["Area 2"]
        Area3 = request.form["Area 3"]
        try:
            mydb = sql.connect(
                host="db4free.net",
                port = 3306,
                user="seifelsayed",
                password="Seif_2001",
                database="p_finder"
            )
            mycursor = mydb.cursor()
            sqls = """
            INSERT INTO person
            VALUES (%s,%s, %s, %s)
            """
            val = (user1,birthdate, age, gender)
            mycursor.execute(sqls,val)
            try:
                sqls = """
                INSERT INTO user_areas_of_focus
                VALUES (%s,%s)
                """
                val = (user1,Area1)
                val1 = (user1,Area2)
                val2 = (user1,Area3)
                mycursor.execute(sqls,val)
                mycursor.execute(sqls,val1)
                mycursor.execute(sqls,val2)
                mydb.commit()
                return render_template('select.html', user = user1, pNums = aPhoneNumbers, citys = cities, projects = projs, list = ammens, types = types)
            except:
                s = "Please Enter unique Values for the areas"
                return render_template('index.html', list = DistinctAreas,message = s)
        except:
            s = "The user already exists"
            return render_template('index.html',list = DistinctAreas, message = s)





@app.route('/review', methods = ['POST', 'GET'])
def review():
    return render_template('review.html', AgentPNums = aPhoneNumbers)        

@app.route('/reviewed', methods = ['POST', 'GET'])
def reviewed():
    if request.method == 'POST':
        num = request.form["AgentSelect"]
        rating = request.form["rating"]
        rev = request.form["rev"]
        try:
            sql3 = """ insert into reviews values (%s, %s, %s, %s)"""
            usr = session.get('user1', None)
            val = (usr,num,rating,rev)
            mycursor.execute(sql3, val)
            mydb.commit()
            return render_template('select.html', message = "Successfully Entered review, Select New Command" , pNums = aPhoneNumbers, citys = cities, projects = projs, list = ammens,  types = types)
        except:
            return render_template('review.html', message = "Already Reviewed this Agent")

@app.route('/viewreview', methods = ['POST', 'GET'])
def veiwRev():
    if request.method == 'POST':
        agent = request.form["AgentSelect2"]
        sql4 = """
            select review from reviews
            where agent_number = {}
            """.format(agent)
        mycursor.execute(sql4)
        reviews = mycursor.fetchall()
        return render_template('reviews.html', reviews = reviews)

@app.route('/return',methods = ['POST', 'GET'])
def ret():
    usr = session.get('user1', None)

    return render_template('select.html', user = usr, pNums = aPhoneNumbers)

@app.route('/viewaggreview',methods = ['POST', 'GET'])
def viewagg():
    try:
        sql5 = """select company_name, avg(r.rating) 
        from agent a join reviews r on(agent_number = phone_number) 
        join broker_company on (company_name = broker_company_name) 
        group by 1;
        """
        mycursor.execute(sql5)
        ratings = mycursor.fetchall()
        headings = ['Company', 'Average Rating']
        return render_template('viewagg.html', list = ratings, headings = headings)
    except:
        return render_template('error.html', message = "An error occured please try again later")





@app.route('/viewDevelopments',methods = ['POST', 'GET'])
def viewdevs():
    if request.method == 'POST':
        proj = request.form['proj']
        try:
            sql6 = """ select d.location, price_from/((MinPropSizesqm+MaxPropSizesqm)/2), prop_type, count(*)  
            from development_project d join property on (proj_name = dev_project_name)  where d.proj_name = "{}" 
            GROUP by 1,2,3""".format(proj)
            mycursor.execute(sql6)
            devList = mycursor.fetchall()
            headings = ["location", "price per sqm", "Type", "Type Count"]
            return render_template("viewDevs.html", headings = headings, list = devList)

        except:
            return render_template('error.html', message = "An error occured please try again later")



@app.route('/selectCityForProps',methods = ['POST', 'GET'])
def cityInProps():
    if request.method == 'POST':
        city = request.form["citySelect"]
        #try:
        mycursor = mydb.cursor()
        sql8 = """ select prop_type, avg(down_pay/SizeSQM) from property where Location = "{}" group by 1""".format(city)
        mycursor.execute(sql8)
        props = mycursor.fetchall()

        headings = ['Property Type', 'average price / sqm']

        mycursor = mydb.cursor()

        sql10 = """ select id, title, prop_type, Bedrooms, Bathrooms, SizeSQM, SizeSQFT, down_pay, ListingDate, Discription, area, Location,
         photo_url from prop_photos join property p on property_id = id 
        where num = 0 and location = "{}" """.format(city)
        mycursor.execute(sql10)
        pics = mycursor.fetchall()

        return render_template("viewProps.html", pics = pics, headings = headings, props = props)
        #except:
        #    return render_template('error.html', message = "An error occured please try again later")

@app.route('/selectAmennitiesForProps', methods = ['POST', 'GET'])
def aggProps():
    if request.method == 'POST':
        a1 = request.form['a1']
        a2 = request.form['a2']
        a3 = request.form['a3']
        min = request.form['min']
        max = request.form['max']
        city = request.form['city']
        sql13 = """ select distinct id, title, prop_type, Bedrooms, Bathrooms, SizeSQM, SizeSQFT, down_pay, ListingDate, Discription, area, Location,
         photo_url from prop_photos join property p on property_id = id join amenities on prop_id = id
        where num = 0 and location = "{}" and down_pay > {} and down_pay < {} and id in(select id from amenities where amenity = "{}" or  amenity = "{}" or  amenity = "{}") """.format(city, min, max, a1, a2, a3)
        mycursor.execute(sql13)
        pics = mycursor.fetchall()
    return render_template("viewAmmen.html", pics = pics)


@app.route("/selectcityforarea", methods = ['POST', 'GET'])
def area10():
    if request.method == "POST":
        city = request.form["city2"]
        type = request.form["type"]
        sql13 = """ select area, avg(down_pay/sizeSQM), count(*)
        from property p
        where prop_type = "{}" and location = "{}" and down_pay != -1 and sizeSQM != -1 group by 1 order by 3,2 limit 10 """.format(type,city)
        mycursor.execute(sql13)
        areas = mycursor.fetchall()
        headings = ['Area',  'Price / sqm','Property Type Count']
        return render_template("view10areas.html", list = areas, headings = headings)


@app.route("/view5bcompanies", methods = ['POST', 'GET'])
def comp5():
    if request.method == "POST":
        sql14 = """
        select  v3.company_name, v3.active_props, v3.emps, AVG(down_pay/sizeSQM) from v3 join agent a 
        on a.broker_company_name = v3.company_name 
        join property2 p on CONVERT(SUBSTRING_INDEX(agent_number,'-',-1),UNSIGNED INTEGER) 
        where down_pay != -1 and sizeSQM != -1 GROUP by v3.company_name order by 2 desc limit 5;
         """
        headings = ["Company Name", "Listing Count", "Agent Count", "Average price per SQM"]
        mycursor.execute(sql14)
        comps = mycursor.fetchall()
        return render_template("comps5.html", headings = headings, list = comps)


@app.route("/selectAgentPhoneNumber", methods = ['POST', 'GET'])
def agents():
    if request.method == "POST":
        agent = request.form["AgentSelect3"]
        sql15 = """ select id, title, prop_type, Bedrooms, Bathrooms, SizeSQM, SizeSQFT, down_pay, ListingDate, Discription, area, Location,
         photo_url from prop_photos join property2 p on property_id = id 
        where num = 0 and agent_number = {} """.format(str(agent))
        mycursor.execute(sql15)
        agentss = mycursor.fetchall()
        return render_template("viewagents.html", pics = agentss)

if __name__ == "__main__":
    app.run(debug = True)