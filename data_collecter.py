class Collector():
    '''handle scraped data'''
    def __init__(self):
        self.data = []

    def __add__(self, data, unique = True):
        if isinstance(data, Collector):
            result_collector = Collector()
            if unique:
                unique_set = set(self.data + data)
                result_collector.set(unique_set)
            else:
                combined_list = self.data + data
                result_collector.set(combined_list)
            return result_collector
        else:
            self.data.append(data)

    def get(self):
        return self.data
    
    def set(self, data):
        if isinstance(data, list):
            self.data = data
        try:
            self.data = list(data)
        except TypeError as e:
            print(f"Error converting non iterable data to list {e}")
