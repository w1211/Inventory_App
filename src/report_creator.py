from src.datamanager import DataManager
import csv
import datetime
import os

class report_creator():
    data_man = DataManager()

    def generate_summary(self, jobs):
        jobs = self.data_man.get_jobs()
        engineers = {e.id: e.get_name() for e in self.data_man.get_engineers()}
        departmnets = self.data_man.departments_as_dict()
        locations = self.data_man.locations_as_dict()

        file_name = 'work_report.csv'.format(datetime.datetime.now().strftime("%H%M%S"))
        file_path = os.path.join('downloads', file_name)


        with open(file_path, 'w', newline='') as csvfile:
            f = csv.writer(csvfile, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)
            f.writerow(["ID", "Equipment Serial", "Engineer", "Job Type","Open Date",
                        "Close Date",'Problem type', "Problems", "Comments/Solutions", "Preventative Work",
                        "Urgency", "Total Cost"])

            for job in jobs:
                f.writerow([job.job_id,
                            job.equipment_serial,
                            engineers[int(job.engineer_id)],
                            job.job_type,
                            job.open_date.date() ,
                            job.close_date.date() if job.close_date else "Ongoing",
                            job.problem_type,
                            job.problems,
                            job.comments_solutions if job.comments_solutions != "" else "None",
                            job.preventative_work if job.preventative_work != "" else "None",
                            job.urgency,
                            job.total_cost
                            ])
        return file_path, file_name


    def generate_cost(self, jobs):
        jobs = self.data_man.get_jobs()
        engineers = {e.id: e.get_name() for e in self.data_man.get_engineers()}
        departmnets = self.data_man.departments_as_dict()
        locations = self.data_man.locations_as_dict()

        file_name = 'purchase_report.csv'#.format(datetime.datetime.now().strftime("%H%M%S"))
        file_path = os.path.join('downloads', file_name)

        with open(file_path, 'w', newline='') as csvfile:
            f = csv.writer(csvfile, delimiter=',', quotechar="'", dialect='excel', quoting=csv.QUOTE_MINIMAL)
            f.writerow(["ID", "Equipment Serial", "Engineer", "Job Type","Open Date",
                        "Close Date",'Problem type', "Problems", "Comments/Solutions", "Preventative Work",
                        "Urgency", "Total Cost", "Purchase", "Cost"])
            for job in jobs:
                for purchase in self.data_man.get_purchases(job.job_id):
                    f.writerow([job.job_id,
                                job.equipment_serial,
                                engineers[int(job.engineer_id)],
                                job.job_type,
                                job.open_date.date(),
                                job.close_date.date() if job.close_date else "Ongoing",
                                job.problem_type,
                                job.problems,
                                job.comments_solutions,
                                job.preventative_work if job.preventative_work != "" or
                                    job.preventative_work is not None else "None",
                                job.urgency,
                                job.total_cost,
                                purchase.item,
                                purchase.cost
                                ])
        return file_path, file_name

