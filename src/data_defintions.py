from sqlalchemy import Column, TEXT, CHAR, BOOLEAN, INTEGER, ForeignKey, ForeignKeyConstraint, \
    DATETIME, DECIMAL

from Inventory_app import database


class Updateable(object):
    def update(self, **vals):
        for param, value in vals.items():
            setattr(self, param, value)


class Department(database.Model):
    __tablename__="departments"
    id = Column(INTEGER,primary_key=True)
    name = Column(TEXT, nullable=False)
    is_deleted = Column(BOOLEAN, nullable=False, default=False)

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def delete(self):
        self.is_deleted = True


class Location(database.Model):
    __tablename__ = "locations"
    id = Column(INTEGER,primary_key=True)
    department = Column(INTEGER, ForeignKey(Department.id), nullable=False)
    name = Column(TEXT, nullable=False)
    is_deleted = Column(BOOLEAN, nullable=False, default=False)

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def delete(self):
        self.is_deleted = True

class Equipment(database.Model, Updateable):

    __tablename__ = "equipment"
    serial_number = Column(TEXT, primary_key=True)
    manufacturer = Column(TEXT, nullable = True)
    model_number = Column(TEXT, nullable = True)
    department = Column(INTEGER, ForeignKey(Department.id),  nullable=False)
    location = Column(INTEGER, ForeignKey(Location.id), nullable = True)
    equipment_type = Column(TEXT, nullable=True)
    condition = Column(CHAR, nullable=False)
    has_user_manual = Column(INTEGER, nullable=False)
    has_service_manual = Column(INTEGER, nullable=False)
    has_open_job = Column(BOOLEAN,  nullable=False)

    def update_has_open_job(self, new_value):
        self.has_open_job = new_value

    def get_serial(self):
        return self.serial_number

    def get_model(self):
        return self.model_number

    def get_department(self):
        return self.department

    def get_location(self):
        return self.location

class Engineer(database.Model):
    id= Column(INTEGER,primary_key=True)
    firstname = Column(TEXT, nullable=False)
    secondname = Column(TEXT, nullable=False)
    is_active = Column(BOOLEAN, nullable=False) # Marks if engo can have new work assigned to them

    def get_id(self):
        return self.id

    def get_is_active(self):
        return self.is_active

    def get_name(self):
        return "{} {}".format(self.firstname, self.secondname)

    def get_first(self):
        return self.firstname

    def get_second(self):
        return self.secondname

    def deactivate(self):
        self.is_active = False


class Job(database.Model, Updateable):
    __tablename__="job"
    job_id = Column(INTEGER, primary_key=True)
    equipment_serial = Column(TEXT, ForeignKey(Equipment.serial_number), nullable=False)
    engineer_id = Column(TEXT, ForeignKey(Engineer.id), nullable=False)
    job_type = Column(TEXT, nullable= False)
    is_closed = Column(BOOLEAN, nullable=False)
    open_date = Column(DATETIME, nullable=False) #TODO convert to date
    close_date = Column(DATETIME, nullable=True)
    problems = Column(TEXT,nullable = False)
    comments_solutions = Column(TEXT, nullable = True)
    preventative_work = Column(TEXT, nullable= True)
    problem_type = Column(TEXT,nullable = False)
    urgency = Column(INTEGER, nullable=False)
    total_cost = Column(DECIMAL, nullable=False, default=0)



    def get_id(self):
        return self.job_id

    def get_cost(self):
        return self.total_cost


class Purchase(database.Model, Updateable):
    __tablename__='purchase'
    id = Column(INTEGER, primary_key=True)
    job_id = Column(INTEGER, ForeignKey(Job.job_id), nullable=False)
    item = Column(TEXT, nullable=False)
    cost = Column(TEXT, nullable=False)

    def get_item(self):
        return self.item

    def get_cost(self):
        return self.cost

    def get_job_id(self):
        return self.job_id

