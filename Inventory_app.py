import os
from flask import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.serial_generator import SerialGenerator
from src.UserManager import UserManager
from src.allowed_values import *


inventory_app = Flask(__name__)
inventory_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # TODO: Change to false when deploying
inventory_app.secret_key = os.urandom(12)

inventory_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'database.db')
database = SQLAlchemy(inventory_app)
inventory_app.secret_key = os.urandom(12)

from src.datamanager import *
from src.report_creator import report_creator

database.create_all()
data_man = DataManager()
user_man = UserManager()


###############################
# Home
###############################
@inventory_app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    open_work = data_man.get_open_jobs()
    return render_template('home.html', open_work=open_work)


###############################
# Login
###############################
@inventory_app.route('/login', methods=['post', 'get'])
def login():
    error = None
    if request.method == 'POST':
        cur_user = user_man.get_user(request.form['username'])
        if not cur_user:
            error = "User not found"
        else:
            if user_man.verify_pass(cur_user, request.form['password']):
                session['logged_in'] = True
                return redirect(url_for('home'))
            else:
                error = "Incorrect password, try again"

    return render_template("login.html", error=error)


###############################
# New Work
###############################
@inventory_app.route('/new_work', methods=['GET', 'POST'])
def new_work():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    result = None
    error_message = ""
    input_query = ""
    if request.method == "POST":
        if "serial_submit" in request.form:
            return redirect(url_for('update_work_item', sn=request.form['serial_submit']))
        else:
            result = data_man.query_sn(request.form['serial_number_search'])
            if not result:
                error_message = "Sorry, no equipment has been found with that serial number. Please check for typos or"\
                        + " create a new device"

        input_query = request.form['serial_number_search']
    return render_template('new_work.html', result=result, error_message=error_message, query=input_query, data_man=data_man)


###############################
# Update work item
###############################
@inventory_app.route('/update_work_item/<sn>', methods=['GET', 'POST'])
def update_work_item(sn):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    item = data_man.query_sn(sn)
    job = None
    num_purchases = 5  # Max number of purchases that can be associated with a job

    if not item:
        return render_template('update_work_item.html', sn_not_found=True)

    purchases = None
    if item.has_open_job:
        job = data_man.get_equipment_open_job(item.serial_number)
        purchases = data_man.get_purchases(job.job_id)

    if request.method == "GET":
        return(render_template('update_work_item.html',
                               item=item,
                               job=job,
                               problem_type=problem_types,
                               job_types=job_types,
                               job_urgency=job_urgency,
                               equipment_problems=data_man.get_serial_problems(item.get_serial()),
                               model_problems=data_man.get_model_problems(item.get_model()),
                               purchases=purchases,
                               num_purchases=num_purchases,
                               engineers=data_man.get_active_engineers(),
                               conditions=equipment_conditions,
                               ))

    else:
        if "cancel" in request.form:
            return redirect(url_for('home'))

        # if not canceling, need to prep variables to either create new job or update existing
        work_completed = False
        open_job = True
        close_date = None
        open_date = datetime.strptime(request.form['open_date'], "%Y-%m-%d").date()

        if request.form["submit"] == "submit_complete":
            work_completed = True
            open_job= False
            now = datetime.now()
            close_date = now
            item.update(has_open_job=False)

        # process any new or changed purchases
        cost = 0
        purchases = []
        for i in range(num_purchases):
            id_str = "p_id_{}".format(i)
            cur_purchase = request.form['purchase_{}'.format(i)]
            cur_cost = request.form['cost_{}'.format(i)].replace(",", "")

            purchases.append((request.form.get("p_id_{}".format(i), None, type=int),
                              cur_purchase,
                              cur_cost
                              ))
            if cur_cost != "":
                cost += float(cur_cost)

        fields = dict(equipment_serial=item.serial_number,
                      engineer_id=request.form['engineer_id'],
                      job_type=request.form['job_type'],
                      is_closed=work_completed,
                      open_date=open_date,
                      close_date=close_date,
                      problems=request.form['problems'],
                      comments_solutions=request.form['comments_solutions'],
                      preventative_work=request.form['preventative_work'],
                      problem_type=request.form['problem_type'],
                      urgency=request.form['job_urgency'],
                      total_cost=cost)

        job_id = None
        if job:
            job_id = data_man.save_update_open_job(job.get_id(), **fields)
        else:
            job_id = data_man.create_new_job(**fields)

        for cur_id, cur_purchase, cur_cost in purchases:
            if cur_id:
                if cur_cost == "" and cur_purchase == "":
                    data_man.delete_purchase(cur_id)

                else:
                    data_man.save_upade_purch(cur_id,
                                              item=cur_purchase,
                                              cost=cur_cost)

            else:
                if cur_purchase != "":
                    data_man.create_purchase(job_id,
                                             cur_purchase,
                                             cur_cost
                                             )

        data_man.save_and_update_equipment(item.get_serial(),
                                           has_open_job= open_job,
                                           condition=request.form['condition'])

        return redirect(url_for('home'))


###############################
# New device
###############################


@inventory_app.route('/new_device', methods=["GET", "POST"], strict_slashes=True)
def new_device():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == "GET" and request.args.get("sn", False, type=str) is False:
        return render_template('new_device.html',
                               condtions=equipment_conditions,
                               types=equipment_types,
                               serial_verified=False)

    elif "Submit" in request.form:
        if 'serial_generated' in request.form:
            sg = SerialGenerator()
            sg.confirm_used(request.form['Serial'])

        details = dict(model_number=request.form['Model'],
                      manufacturer=request.form['Manufacturer'],
                      department=request.form['Department'],
                      location=request.form['Location'],
                      equipment_type=request.form['Equipment'],
                      condition=request.form['Condition'],
                      has_user_manual=request.form['User_manual'],
                      has_service_manual=request.form['Service_manual'])

        if 'is_update' in request.form:
            data_man.update_item(request.form['Serial'], **details)
            return redirect(url_for("inventory"))

        else:
            details.update({'serial_number':request.form['Serial'], 'has_open_job':False })
            data_man.new_item(**details)
            return redirect(url_for('update_work_item', sn=request.form['Serial']))

    else:
        serial_generated = False
        serial_query = None
        serial_verified = False


        if "generate_serial" in request.form:
            sg = SerialGenerator()
            serial_query = sg.get_serial()
            serial_verified = True
            serial_generated = True

        elif "verify_serial" in request.form:
            serial_query = request.form['Serial']
            result = data_man.query_sn(serial_query)
            serial_verified = True  # verified as NOT existing, i.e. verified as valid input

            if result:
                serial_verified = False

        departments = data_man.get_departments(False)
        locations = None
        item = None

        if request.args.get("sn", False, type=str) is not False:
            serial_query = request.args.get("sn", type=str)
            item = data_man.query_sn(serial_query)
            locations = data_man.get_locations(item.get_department(), False)
            serial_verified = True

        return render_template('new_device.html',
                               condtions=equipment_conditions,
                               types=equipment_types,
                               serial_verified=serial_verified,
                               serial_query=serial_query,
                               serial_generated=serial_generated,
                               departments=departments,
                               locations=locations,
                               item=item)


###############################
# Inventory
################################
@inventory_app.route('/inventory', methods=["get", "post"])
def inventory():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    fields = [(attr, attr.replace("_"," ").title()) for attr in dir(Equipment) if not callable(getattr(Equipment,attr)) \
              and not attr.startswith("_") and attr not in ['query','metadata']]

    items = None
    if request.method == "POST":
        attr = getattr(Equipment, request.form["field"])
        items = data_man.search_items(attr, request.form['search'])
    else:
        items = data_man.get_invenotry()

    return render_template('inventory.html',
                           items=items,
                           depart_dict = data_man.departments_as_dict(),
                           location_dict = data_man.locations_as_dict,
                           equipment_conditions=equipment_conditions,
                           fields=fields)


###############################
# Manage engineers
################################
# Todo add confrimation message when deactivating engo

@inventory_app.route('/manage_engineers', methods=["GET", "POST"])
def manage_engineers():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == "POST":
        if "add_engo" in request.form:
            data_man.new_engineer(request.form['firstname'],
                                  request.form['secondname']
                                  )
        else:
            data_man.deactivate_engineer(request.form['delete_engo'])

    return render_template("manage_engineers.html", engineers=data_man.get_active_engineers())


################################
# Manage Departments
################################

@inventory_app.route('/manage_departments', methods=['Get', 'Post'])
def manage_departments():
    if not session.get('logged_in'):
        pass  # TODO FIX ME return redirect(url_for('login'))

    error = None
    if request.method == "POST":
        submit_value = request.form.get('submit', None)  # value is either a string, or the id of the department
        if submit_value == 'new_department':             # that is going to have the new location added to it
            name =  request.form['dept_name']
            if name == "":
                error = "Department name cannot be empty"
            else:
                data_man.new_department(request.form['dept_name'])

        elif submit_value is not None:
            name = request.form[str(submit_value)]
            if name == "":
                error = "Location name cannot be empty"
            else:
                data_man.new_location(request.form[str(submit_value)],  # loc name is entered in an input with
                                  submit_value)                     # name=Dept_id

        elif "remove_department" in request.form:
            data_man.remove_department(request.form['remove_department'])

        else:
            data_man.remove_loc(request.form['remove_location'])

    return render_template('manage_departments.html',
                           departments=data_man.get_departments(False),
                           data_man=data_man,
                           error=error)


###############################
# Log out
################################
@inventory_app.route('/work_history')
def work_history():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    sn = request.args.get("sn", None, type=str)
    item = data_man.query_sn(sn)

    return render_template("work_history.html",
                            item=item,
                            equipment_problems=data_man.get_serial_problems(sn),
                            model_problems = data_man.get_model_problems(item.model_number),
                            job=None,
                            data_man=data_man)

###############################
# Log out
################################
@inventory_app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


###############################
# Update locs
################################
@inventory_app.route('/update_locations', methods=['Get', 'Post'])
def update_locations():
    dep_id = request.args.get('dep_id', 0, type=int)
    locs = [(l.get_id(), l.get_name()) for l in data_man.get_locations(dep_id, False)]
    return jsonify(locs)


###############################
# Work Report
################################

@inventory_app.route('/downloads', methods=['Get', 'Post'])
def downloads():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    elif request.method == "POST":
        #do stuff
        rc = report_creator()
        jobs = data_man.get_jobs()
        path = ""
        name = ""
        if "inventory" in request.form:
            pass
        elif "summary" in request.form:
            path, name = rc.generate_summary(jobs)
        elif "cost" in request.form:
            path, name = rc.generate_cost(jobs)

        return send_file(path, attachment_filename=name, as_attachment=True)

    return render_template('downloads.html')


#########

###############################
# Downlaod
################################
@inventory_app.route('/download_summary')
def download_summary():
    rc = report_creator()
    jobs =  data_man.get_jobs()
    path, name = rc.generate_summary(jobs)
    return redirect(url_for('download_file', file=path))

@inventory_app.route('/download_cost')
def download_cost():
    rc = report_creator()
    jobs =  data_man.get_jobs()
    path, name = rc.generate_cost(jobs)
    return send_file(path, attachment_filename=name, as_attachment=True)


@inventory_app.route('/download_file/<file>')
def download_file(file):
    return send_file(file, as_attachment=True)


###############################
# Error handling
################################
@inventory_app.errorhandler(404)
def page_not_found(*_):  # *_ is just to ignore the exception variable passed to the errorhandler
    return render_template('404.html'), 404


@inventory_app.errorhandler(500)
def page_not_found(*_):
    return render_template('500.html'), 500
