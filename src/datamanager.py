from Inventory_app import database
from src.data_defintions import *
import pickle

class DataManager():

    ###############################
    # Item functions
    ################################

    def __init__(self):
        self._engine = database.engine
        self._DBsession= database.session


    def check_exists(self, serial_num):
        res = self._DBsession.query(Equipment).filter(Equipment.serial_number == serial_num)
        if res:
            return True
        return False


    def new_item(self, **details):
        new_item = Equipment(**details)
        self._DBsession.add(new_item)
        self._DBsession.commit()
        self._DBsession.close()
        return

    def query_sn(self, sn): #finds a single item and returns it
        session = self._DBsession()
        result= session.query(Equipment).filter(Equipment.serial_number == sn).one_or_none()
        if result:
            session.expunge(result)
        session.close()
        return result

    def save_and_update_equipment(self, sn, **to_update):
        equip = self._DBsession.query(Equipment).filter(Equipment.serial_number == sn).one_or_none()
        if equip:
            equip.update(**to_update)
            self._DBsession.commit()
            self._DBsession.close()
        return equip

    def get_invenotry(self):
        session = self._DBsession()
        inven = session.query(Equipment).all()
        session.close()
        return inven

    def update_item(self, sn, **kwargs):
        session = self._DBsession()
        result = session.query(Equipment).filter(Equipment.serial_number == sn).one_or_none()
        result.update(**kwargs)
        session.commit()
        session.close()

    def search_items(self, attr, value):
        session = self._DBsession()
        result = session.query(Equipment).filter(attr.like(value)).all()
        session.close()
        return result

    ###############################
    # Job functions
    ################################

    def create_new_job(self, **details):
        new_job=Job(**details)
        self._DBsession().add(new_job)
        self._DBsession.commit()
        jid = new_job.get_id()
        self._DBsession.close()
        self._DBsession.add(new_job)
        return jid


    def get_jobs(self):
        return self._DBsession.query(Job).all()

    def get_all_jobs(self, sn):
        return self._DBsession.query(Job).filter(Job.equipment_serial==sn)

    def get_open_jobs(self):
        return self._DBsession.query(Job).filter(Job.is_closed==0)

    def get_closed_jobs(self):
        return self._DBsession.query(Job).filter(Job.is_closed==1)

    def save_update_open_job(self, job_id, **details):
        job = self._DBsession.query(Job).filter(Job.job_id == job_id).one_or_none()
        jid = job.get_id()
        if job:
            job.update(**details)
            self._DBsession.commit()
            self._DBsession.expunge(job)
            self._DBsession.close()
        return jid

    def get_equipment_open_job(self, serial): #TODO Test you can only have one open job
        return self._DBsession.query(Job).filter(Job.equipment_serial == serial, Job.is_closed == False).one_or_none()

    def get_serial_problems(self, serial): #returns an tuple of tuples (problems, comments/solution] for this model
        session = self._DBsession()
        results = session.query(Job).filter(Job.equipment_serial == serial).all()
        session.close()
        return results

    def get_model_problems(self, model):
        equipment = self._DBsession().query(Equipment).filter(Equipment.model_number==model) #get all equipment of certain model
        serials = [equip.get_serial() for equip in equipment]
        jobs = self._DBsession().query(Job).filter(Job.equipment_serial.in_(serials)).all()
        self._DBsession.close()
        return jobs

    ###############################
    # Engo Functions
    ################################

    def new_engineer(self, firstname, secondname):
        new_engineer = Engineer(firstname=firstname, secondname=secondname, is_active=True)
        session = self._DBsession()
        session.add(new_engineer)
        session.commit()
        session.close()

    def get_engineers(self):
        session = self._DBsession()
        engineers = session.query(Engineer).all()
        session.close()
        return engineers

    def get_engineer(self, eng_id):
        session= self._DBsession()
        engineer = session.query(Engineer).filter(Engineer.id == eng_id).one_or_none()
        session.expunge(engineer)
        session.close()
        return engineer

    def get_active_engineers(self):
        session = self._DBsession()
        engineers = session.query(Engineer).filter(Engineer.is_active == True)
        session.close()
        return engineers

    def deactivate_engineer(self, eng_id):
        session= self._DBsession()
        engineer = session.query(Engineer).filter(Engineer.id == eng_id).one_or_none()
        engineer.deactivate()
        session.commit()
        session.close()


    ###############################
    # Purchase Functions
    ################################

    def create_purchase(self, job_id, item, cost):
        new_p = Purchase(job_id=job_id, item=item, cost=cost)
        session = self._DBsession()
        session.add(new_p)
        session.commit()
        session.close()
        return new_p

    def save_upade_purch(self,p_id, **details):
        session = self._DBsession()
        purchase = session.query(Purchase).filter(Purchase.id == p_id).one_or_none()
        if purchase:
            purchase.update(**details)
            self._DBsession.commit()
            self._DBsession.expunge(purchase)
            self._DBsession.close()
        return purchase

    def get_purchases(self, job_id):
        session = self._DBsession()
        purchases = session.query(Purchase).filter(Purchase.job_id == job_id).all()
        session.close()
        return purchases

    def delete_purchase(self, id):
        session = self._DBsession()
        to_delete = session.query(Purchase).filter(Purchase.id == id).one_or_none()
        session.delete(to_delete)
        session.commit()
        session.close()

    ###############################
    # Department Functions
    ################################

    def get_department_name(self, id):
        session = self._DBsession()
        deps = session.query(Department).filter(Department.id==id).one_or_none()
        session.close()
        return deps.name

    def get_departments(self, inc_deleted):
        session = self._DBsession()
        deps = session.query(Department).filter(Department.is_deleted==inc_deleted).all()
        session.close()
        return deps

    def new_department(self, name):
        department = Department(name=name)
        session = self._DBsession()
        session.add(department)
        session.commit()
        session.close()

    def remove_department(self, id):
        session = self._DBsession()
        dep =  session.query(Department).filter(Department.id==id).one_or_none()
        dep.delete()
        session.commit()
        session.close()

    def departments_as_dict(self):
        session = self._DBsession()
        deps = session.query(Department).all()
        return {d.get_id(): d.get_name() for d in deps}


    ###############################
    # Department Functions
    ################################

    def get_locations(self, dep_id, inc_deleted):
        session = self._DBsession()
        locs = session.query(Location).filter(Location.department == dep_id, Location.is_deleted==inc_deleted)
        session.close()
        return locs

    def get_location_name(self, loc):
        session = self._DBsession()
        locs = session.query(Location).filter(Location.id == loc).one_or_none()
        session.close()
        return locs.name

    def new_location(self, name,dep_id):
        loc = Location(name=name, department=dep_id)
        session = self._DBsession()
        session.add(loc)
        session.commit()
        session.close()

    def remove_loc(self, id):
        session = self._DBsession()
        loc =  session.query(Location).filter(Location.id==id).one_or_none()
        loc.delete()
        session.commit()
        session.close()

    def locations_as_dict(self):
        session = self._DBsession()
        loc = session.query(Location).all()
        return {l.get_id(): l.get_name() for l in loc}