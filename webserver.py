from flask import Flask, url_for, request, render_template, g
import sqlite3
import datetime

app = Flask(__name__)
DATABASE = 'Parkanlage.db'

# init DB
def get_db():
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        return db

# close DB
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

# select data from database
def select_db(query, args=(), one = False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv # return the first entry if "one" is set, else return all 

# insert data into database
def modify_db(query):
    db = get_db()
    cur = db.cursor()
    cur.execute(query)
    db.commit()
    db.close()

def is_table_empty(tableName):
    result = select_db("SELECT * FROM " + str(tableName), (), True)
    if result == None:
        return True
    else:
        return False


## Routing

@app.route("/")
@app.route("/index")
def index(): #index html
    return render_template('index.html',
        project_path=url_for("project_main"), 
        req_path=url_for("requirements"))
        # add params here

@app.route("/requirements") # requirements for the project
def requirements():
    return render_template('requirements.html')

@app.route("/project_main", methods= ['GET', 'POST']) # main page
def project_main():
        if request.method == 'POST':
                licenseplate = request.form['licenseplate']

                if not is_table_empty("KennzeichenBuffer"):
                        modify_db("DELETE FROM KennzeichenBuffer")
                
                modify_db("INSERT INTO KennzeichenBuffer VALUES (\""+ licenseplate + "\")")

                if 'drivein' in request.form:
                        # prüfe, ob Fahrer bereits existiert
                        UserID = GetUserIDFromLicensePlate(licenseplate)
                        if UserID > -1:
                                print("User is registered")
                                return CheckForFreePlace(licenseplate, IsDriverCardUser(UserID))

                        else: # Fahrer ist neu
                                # Abfrage auf Dauerkarte y / n 
                                return project_drivein()
                        
                elif 'driveout' in request.form:
                        return project_driveout(licenseplate)

        return render_template('project_main.html')

@app.route("/project_drivein", methods= ['GET', 'POST']) # drive in page (not registered)
def project_drivein():
        if request.method == 'POST':
                licenseplate = ""
                for result in select_db("SELECT ID FROM KennzeichenBuffer"):
                        licenseplate = result['ID']     

                if 'card' in request.form:
                        # Insert into DB new Fahrer with Drivercard
                        if is_table_empty("Fahrer"):
                                modify_db("INSERT INTO Fahrer VALUES (1, 1)")
                        else:
                                modify_db("INSERT INTO Fahrer VALUES ((SELECT MAX(ID) FROM Fahrer) + 1, 1)")

                        #INSERT INTO Fahrerauto VALUES ((SELECT MAX(ID) FROM Fahrer), "Kennzeichen")
                        modify_db("INSERT INTO Fahrerauto VALUES ((SELECT MAX(ID) FROM Fahrer), \"" + licenseplate + "\")")

                        modify_db("DELETE FROM KennzeichenBuffer")
                        return CheckForFreePlace(licenseplate, True)

                elif 'ticket' in request.form:
                        # Insert into DB new Fahrer without Drivercard
                        if is_table_empty("Fahrer"):
                                modify_db("INSERT INTO Fahrer VALUES (1, 0)")
                        else:
                                modify_db("INSERT INTO Fahrer VALUES ((SELECT MAX(ID) FROM Fahrer) + 1, 0)")

                        #INSERT INTO Fahrerauto VALUES ((SELECT MAX(ID) FROM Fahrer), "Kennzeichen")
                        modify_db("INSERT INTO Fahrerauto VALUES ((SELECT MAX(ID) FROM Fahrer), \"" + licenseplate + "\")")

                        modify_db("DELETE FROM KennzeichenBuffer")
                        return CheckForFreePlace(licenseplate, False)

        return render_template('project_drivein.html')

@app.route("/project_driveout", methods= ['GET', 'POST']) # drive out pages + handling
def project_driveout(licenseplate = None):
        if licenseplate is not None:
                modify_db("DELETE FROM KennzeichenBuffer")
                UserID = GetUserIDFromLicensePlate(licenseplate)
                carduser = IsDriverCardUser(UserID)
        
                #UPDATE Parker SET Ausfahrtszeitpunkt = "Datetime.Now" WHERE Kennzeichen = "Kennzeichen" AND Ausfahrtszeitpunkt = "NULL"
                query = "UPDATE Parker SET Ausfahrtszeitpunkt = \"" + str(datetime.datetime.now()) + "\" WHERE Kennzeichen = \"" + str(licenseplate) + "\" AND Ausfahrtszeitpunkt = \"NULL\""
                modify_db(query)

                if carduser:
                        return render_template("project_driveout_card.html")
                else:
                        return render_template("project_driveout_ticket.html", value_to_pay='123€') #für weitere Implementation hier Methode für Preis einbauen

        if request.method == 'POST':
                if 'pay' in request.form:
                        return render_template("project_driveout_ticket_payed.html")


# Helper functions                

# Returns True if the User has a DriverCard
def IsDriverCardUser(UserID):
        resultDB = -1

        query = "SELECT * FROM FAHRER WHERE ID = " + str(UserID)
        for driver in select_db(query):
                resultDB = driver['Dauerkarte']

        if resultDB == 1:
                return True
        else:
                return False

# Returns UserID if one Exists, else -1
def GetUserIDFromLicensePlate(Licenseplate): 
        resultDB = -1

        query = "SELECT * FROM Fahrerauto WHERE Kennzeichen = \""+ str(Licenseplate) + "\""
        for vehicle in select_db(query):
                resultDB = vehicle['FahrerID']

        return resultDB

# Returns True if a Place is free for the User, else False
def IsPlaceFree(DriverIsCardUser):
        resultDB = 0

        for places in select_db('SELECT COUNT(Parker.Kennzeichen) AS Anzahl FROM Parker ' +
                                'LEFT JOIN Fahrerauto ON Fahrerauto.Kennzeichen = Parker.Kennzeichen ' +
                                'LEFT JOIN Fahrer ON Fahrer.ID = Fahrerauto.FahrerID ' +
                                'WHERE Parker.Ausfahrtszeitpunkt = "NULL" AND Fahrer.Dauerkarte = 1'):
                resultDB = places['Anzahl']
        
        quantityFreeSpacesCard = 40 - int(resultDB)

        for places in select_db('SELECT COUNT(Parker.Kennzeichen) AS Anzahl FROM Parker ' +
                                'LEFT JOIN Fahrerauto ON Fahrerauto.Kennzeichen = Parker.Kennzeichen ' +
                                'LEFT JOIN Fahrer ON Fahrer.ID = Fahrerauto.FahrerID ' +
                                'WHERE Parker.Ausfahrtszeitpunkt = "NULL" AND Fahrer.Dauerkarte = 0'):
                resultDB = places['Anzahl']

        quantityFreeSpacesTicket = 140 - int(resultDB)

        if DriverIsCardUser:
                return (quantityFreeSpacesCard + quantityFreeSpacesTicket)
        else:
                return quantityFreeSpacesTicket

# Returns the HTML File for the User, Valid if a Place is free, Invalid if not
def CheckForFreePlace(Licenseplate, DriverIsCardUser):
        count = IsPlaceFree(DriverIsCardUser)
        isFree = False
        
        if DriverIsCardUser:
                isFree = count > 0
        else:
                isFree = count >= 4

        if isFree:
                # INSERT INTO Parker VALUES((SELECT MAX(ID) FROM Parker) + 1, "Kennzeichen", "Datetime.Now", "NULL")
                if is_table_empty("Parker"):
                        query = "INSERT INTO Parker VALUES(1, \"" + str(Licenseplate) + "\",\"" + str(datetime.datetime.now()) + "\",\"NULL\")"
                else:
                        query = "INSERT INTO Parker VALUES((SELECT MAX(ID) FROM Parker) + 1, \"" + str(Licenseplate) + "\",\"" + str(datetime.datetime.now()) + "\",\"NULL\")"
                                
                modify_db(query)

                if(DriverIsCardUser):
                        return render_template("project_drivein_valid.html")
                else:
                        return render_template("project_drivein_valid.html", free_places=("Freie Plätze: " + str(count)))

        else:
                return render_template("project_drivein_invalid.html")
        

# Main start
if __name__ == '__main__':
    app.run(port=4698, debug=True)