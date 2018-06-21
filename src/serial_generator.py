import pickle


class SerialGenerator():

    # Creates serials by reading the next available serial from a pickle file
    # For single serial requests it needs to be confirmed that the serial was used
    # For batch request, its assumed that all the srials are used

    def get_serial(self):
        num = self._load_num()
        serial = self._format(num)
        return serial


    def confirm_used(self, serial):
        self._save_num(int(serial[4:])+1)


    def _load_num(self):
        num = None
        with open('./data/serial.dat', 'rb') as f:
            num = pickle.load(f)
        return num

    def _save_num(self,num):
        with open('./data/serial.dat', 'wb') as f:
            pickle.dump(num,f,protocol=2)

    def _format(self, num):
        return "GEN-{}".format(num)

    def get_list(self,n):
        num = self._load_num()
        return [self._format(i) for i in range(num,num+n)]