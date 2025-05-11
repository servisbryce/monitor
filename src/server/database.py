'''

    We aim to provide a simple interface for interacting with a database through a key-value store schema.

'''

import json, time, dbm

# Define a default unpopulated unserialized database record.
default_schema = {

    # Store the metadata pertaining to the record.
    "metadata": {

        # Store various timestamps pertaining to the record.
        "created_at": None,
        "updated_at": None,

        # Store logs of events that have changed the state of the record.
        "audit_log": []

    },

    # Store the actual data pertaining to the record.
    "data": {

        # Here, we'll store various analytics regarding the client that the client self-reports to us.
        "analytics": {

            # Collect basic networking information regarding the client. 
            "network": {

                # Store network latency as well.
                "latency": None,

                # Store the interfaces of the client and various information regarding them in a table.
                "interfaces": []

            },

            # Store various analytics regarding the processor of the client.
            "cpu": {

                "threads": None,
                "cores": None,
                "model": None,
                "load": None

            },

            # Store various analytics regarding the memory of the client.
            "memory": {

                # Store the amount of memory available and used on the client.
                "available": None,
                "used": None,

                # If swapping is enabled on the client, we'll store the swap information in a table here.
                "swap": None

            },

            # Store various analytics regarding the storage of the client.
            "disks": {

                # Store tables regarding the data of various mounted disks on the client.
                "mounting_points": [] 

            }

        }

    }

}

# Define the sub-schema for the network interfaces for documentation purposes.
default_network_interface_schema = {

    "name": None,
    "ipv6": None,
    "ipv4": None,
    "mac": None 

}

# Define the sub-schema for the CPU for documentation purposes.
default_cpu_schema = {

    "threads": None,
    "cores": None,
    "model": None,
    "load": None

}

# Define the sub-schema for memory and swap memory for documentation purposes.
memory_schema = {

    "available": None,
    "used": None,
    "swap": None,

}

# Define a class to represent a record in the database.
class Record:

    # We aim to use this class to load an existing record from the database or create a new one if it doesn't exist.
    def __init__(self, token):

        # Store the token in the record class.
        self.token = token

        # This must be kept always unserialized to be used later.
        self.record = None

        # Attempt to load the database file.
        with dbm.open("monitor.sqlite", "c") as database:

            # Attempt to retrieve the client record from the database, if it exists.
            try:

                # Check if there is a record of the client in the database already and deserialize it.
                serialized_record = database[self.token]
                self.record = json.loads(serialized_record)

            # If the record doesn't exist, we'll create a new one.
            except KeyError:
                # Copy the default schema into our record variable.
                self.record = default_schema

                # Update the record.
                self.record["metadata"]["created_at"] = time.time()
                self.record["metadata"]["updated_at"] = time.time()
                self.record["metadata"]["audit_log"].append({

                    "timestamp": time.time(),
                    "description": "A new record was generated.",
                    "event": "created_record"

                })

                # Serialize the record.
                serialized_record = json.dumps(self.record)

                # Add the record to the database.
                database[self.token] = serialized_record
    
    # This function will be used to either edit or add a new network latency to the record.
    def set_network_latency(self, latency):
        # Update the record.
        self.record["data"]["analytics"]["network"]["latency"] = latency

        # Update the record metadata.
        self.record["metadata"]["updated_at"] = time.time()
        self.record["metadata"]["audit_log"].append({

            "timestamp": time.time(),
            "description": "Network latency was updated.",
            "event": "network_latency_updated"

        })

        # Serialize the record and update the database.
        with dbm.open("monitor.sqlite", "c") as database:

            # Serialize the record.
            serialized_record = json.dumps(self.record)

            # Update the record in the database.
            database[self.token] = serialized_record

    # This function will be used to either edit or add a new network interface to the record.
    def set_network_interfaces(self, interface):

        if (len(self.record["data"]["analytics"]["network"]["interfaces"]) > 0):

            # Check if the interface name is already an object inside of the interface list.
            for interface_record in self.record["data"]["analytics"]["network"]["interfaces"]:

                # If the interface name is already in the list, we'll update that record.
                if interface["name"] == interface_record["name"]:

                    # Update the record.
                    interface_record["ipv6"] = interface["ipv6"]
                    interface_record["ipv4"] = interface["ipv4"]
                    interface_record["mac"] = interface["mac"]
                    break

                else:

                    # If the interface name is not in the list, we'll add it to the list.
                    self.record["data"]["analytics"]["network"]["interfaces"].append(interface)
                    break
        
        else:
            # If the interface list is empty, we'll add the interface to the list.
            self.record["data"]["analytics"]["network"]["interfaces"].append(interface)

        # Update the record metadata.
        self.record["metadata"]["updated_at"] = time.time()
        self.record["metadata"]["audit_log"].append({

            "timestamp": time.time(),
            "description": "Network interface " + interface["name"] + " was updated.",
            "event": "network_interface_updated"

        })

        # Serialize the record and update the database.
        with dbm.open("monitor.sqlite", "c") as database:

            # Serialize the record.
            serialized_record = json.dumps(self.record)

            # Update the record in the database.
            database[self.token] = serialized_record

    def set_cpu(self, cpu):
        
        # Update the record.
        self.record["data"]["analytics"]["cpu"]["threads"] = cpu["threads"]
        self.record["data"]["analytics"]["cpu"]["cores"] = cpu["cores"]
        self.record["data"]["analytics"]["cpu"]["model"] = cpu["model"]
        self.record["data"]["analytics"]["cpu"]["load"] = cpu["load"]

        # Update the record metadata.
        self.record["metadata"]["updated_at"] = time.time()
        self.record["metadata"]["audit_log"].append({

            "timestamp": time.time(),
            "description": "CPU information was updated.",
            "event": "cpu_updated"

        })

        # Serialize the record and update the database.
        with dbm.open("monitor.sqlite", "c") as database:

            # Serialize the record.
            serialized_record = json.dumps(self.record)

            # Update the record in the database.
            database[self.token] = serialized_record

    def set_memory(self, memory):

        # Update the record.
        self.record["data"]["analytics"]["memory"]["available"] = memory["available"]
        self.record["data"]["analytics"]["memory"]["used"] = memory["used"]
        self.record["data"]["analytics"]["memory"]["swap"] = memory["swap"]

        # Update the record metadata.
        self.record["metadata"]["updated_at"] = time.time()
        self.record["metadata"]["audit_log"].append({

            "timestamp": time.time(),
            "description": "Memory information was updated.",
            "event": "memory_updated"

        })

        # Serialize the record and update the database.
        with dbm.open("monitor.sqlite", "c") as database:

            # Serialize the record.
            serialized_record = json.dumps(self.record)

            # Update the record in the database.
            database[self.token] = serialized_record

    def set_disk_mounting_point(self, mounting_point):

        if (len(self.record["data"]["analytics"]["disks"]["mounting_points"]) > 0):

            # Check if the path is already an object inside of the path list.
            for mounting_point_record in self.record["data"]["analytics"]["network"]["mounting_points"]:

                # If the path name is already in the list, we'll update that record.
                if mounting_point["path"] == mounting_point_record["path"]:

                    # Update the record.
                    mounting_point_record["available"] = mounting_point["available"]
                    mounting_point_record["used"] = mounting_point["used"]
                    break

                else:

                    # If the mounting point is not in the list, we'll add it to the list.
                    self.record["data"]["analytics"]["disks"]["mounting_points"].append(mounting_point)
                    break
        
        else:
            # If the mounting point list is empty, we'll add the mounting point to the list.
            self.record["data"]["analytics"]["disks"]["mounting_points"].append(mounting_point)

        # Update the record metadata.
        self.record["metadata"]["updated_at"] = time.time()
        self.record["metadata"]["audit_log"].append({

            "timestamp": time.time(),
            "description": "Mounting point " + mounting_point["name"] + " was updated.",
            "event": "network_interface_updated"

        })

        # Serialize the record and update the database.
        with dbm.open("monitor.sqlite", "c") as database:

            # Serialize the record.
            serialized_record = json.dumps(self.record)

            # Update the record in the database.
            database[self.token] = serialized_record