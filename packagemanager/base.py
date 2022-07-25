from abc import ABC, abstractmethod

class PackageManagerBase(ABC):
    NAME = None

    @staticmethod
    @abstractmethod
    def is_present():
        return False


    @abstractmethod
    def add_sources(self, sources_data):
        pass


    @abstractmethod
    def install_packages(self, package_list):
        pass
