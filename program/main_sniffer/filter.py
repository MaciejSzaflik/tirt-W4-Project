##
## Klasa zarządzająca pamięcią aplikacji. Wysyła powiadomienia do GUI o nowych strumieniach i wysyła kolejne pakiety.
## Wymaga, aby GUI posiadało obsługę:
##    GUI.addStream(key, packetData) - dodawanie nowego strumienia i miniatury
##    GUI.removeStream(key) - usuwanie strumienia i miniatury
##    GUI.nextPacket(key, packetData['body_type'], body) - przesłanie kolejnego pakietu wraz z podaniem typu
##
## Ponadto klasa udostępnia następujące metody dla GUI:
##    onGUISelectStream(key) - zmiana rozmiaru wysyłanego strumienia na większy
##    onGUIUnselectStream(key) - zmiana rozmiaru wysyłanego strumienia na mniejszy
##    onGUISetSize(size, width, height) - zmiana rozdzielczości wyświetlania
##
class dataManager(object):
    filterOptions = {}
    storage = {}
    sizeOptions = {
        'small': {
            width: 300,
            height: 200
        },
        'big': {
            width: 1000,
            height: 800
        }
    }

    def __init__(self):
        self.applyFilter()

    def setFilterValue(self, data, value):
        if not data.get(value, None) == None:
            self.filterOptions[value] = data.get(value, None)

    def setFilter(self, data):
        setFilterValue(data, 'source_addres_start')
        setFilterValue(data, 'source_addres_end')
        setFilterValue(data, 'source_port_start')
        setFilterValue(data, 'source_port_end')

        setFilterValue(data, 'target_addres_start')
        setFilterValue(data, 'target_addres_end')
        setFilterValue(data, 'target_port_start')
        setFilterValue(data, 'target_port_end')
        setFilterValue(data, 'http')

        self.applyFilter()

    def applyFilter(self):
        for key in self.storage
            if not self.checkInFilter(self.storage[key]):
                self.GUIRemoveStream(key)

    def between(self, packetData, name):
        return packetData.get(name + '_start') >= self.get(name + '_start') and packetData.get(name + '_end') <= self.get(name + '_end')

    def equals(self, packetData, name):
        if not packetData.get(name, None) == None:
            return self.filterOptions.get(name) == True
        else
            return False

    def checkInFilter(self, packetData):
        return (self.between(packetData, 'source_addres') and
          self.between(packetData, 'target_addres') and
          self.between(packetData, 'source_port') and
          self.between(packetData, 'target_port') and
          (self.equals(packetData, 'http') or self.equals(packetData, 'rtmp')))

    def saveNewPacket(self, packetData):
        key = self.createKey(packetData)
        self.storage[key] = 'small'
        self.GUIAddStream(key, packetData)

    def createKey(self, packetData):
        return packetData['source']['address'] + str(packetData['source']['port']) + packetData['target']['address'] + str(packetData['target']['port'])

    def checkLocally(self, packetData):
        return self.storage.get(self.createKey(packetData), None) == None

    def resizeBody(self, body, size):
        # somehow resize body witch self.resizeOptions[size]
        return body

    def onGUISelectStream(self, key):
        self.storage[key] = 'big'

    def onGUIUnselectStream(self, key):
        self.storage[key] = 'small'

    def onGUISetSize(self, size, width, height):
        self.sizeOptions[size] = {
            'width': width,
            'height': height
        }

    def GUIAddStream(self, packetData):
        #GUI.addStream(self.createKey(packetData), packetData)
        pass

    def GUIRemoveStream(self, key):
        #GUI.removeStream(key)
        pass

    def notifyGUI(self, packetData):
        key = self.createKey(packetData)
        #GUI.nextPacket(key, packetData['body_type'], self.resizeBody(body, self.storage.get(key)))

    # action to be added in main LOOP of comss
    def receiveData(self, packetData):
        if self.checkLocally(packetData):
            self.notifyGUI(packetData)
        else
            if self.checkInFilter(packetData):
                self.saveNewPacket(packetData)
                self.notifyGUI(packetData)

