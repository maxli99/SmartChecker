import yaml
import json

class NSNG_OSS_config(object):
    def __init__(self):

        #with open('config/OSS_Tables_column.json','r') as file_table:
        #    self.NSNG_OSS_tables_views = json.load(file_table)        
        with open('config/OSS_Tables_column.yaml','r') as file_table:
            self.NSNG_OSS_tables_views = yaml.load(file_table)        

        #with open('config/OSS_Databases.json','r') as file_databases:
        #    self.NSNG_OSS_database = json.load(file_databases)
        with open('config/OSS_Databases.yaml','r') as file_databases:
            self.NSNG_OSS_database = yaml.load(file_databases)

        #with open('config/OSS_NSNG.json','r') as file_ne:
            #    self.NSNG_OSS_NE = json.load(file_ne)
        with open('config/OSS_NSNG.yaml','r') as file_ne:
            self.NSNG_OSS_NE = yaml.load(file_ne)
        
if __name__ == "__main__":
    nsng_oss_configs = NSNG_OSS_config()
    #print 'NSNG_OSS_tables_views:' + str(nsng_oss_configs.NSNG_OSS_tables_views)
    #print 'NSNG_OSS_tables_views.keys():'+str(nsng_oss_configs.NSNG_OSS_tables_views.keys())
    #print "NSNG_OSS_tables_views['MME_OSS_table_view'][0].keys():"+str(nsng_oss_configs.NSNG_OSS_tables_views['MME_OSS_table_view'][0].keys())
    #print "NSNG_OSS_tables_views['MME_OSS_table_view'][0]['tables']['name']:"+str(nsng_oss_configs.NSNG_OSS_tables_views['MME_OSS_table_view'][0]['tables']['name'])
    #print "NSNG_OSS_tables_views['MME_OSS_table_view'][0]['tables']['columns']['column']:"+str(nsng_oss_configs.NSNG_OSS_tables_views['MME_OSS_table_view'][0]['tables']['columns']['column'])
    print 'NSNG_OSS_NE name:'+nsng_oss_configs.NSNG_OSS_database['database'][0]['name']
    print 'NSNG_OSS_NE ip:'+nsng_oss_configs.NSNG_OSS_database['database'][0]['ip']
    print 'NSNG_OSS_NE port:'+nsng_oss_configs.NSNG_OSS_database['database'][0]['port']
    print 'NSNG_OSS_NE db:'+nsng_oss_configs.NSNG_OSS_database['database'][0]['db']
    print 'NSNG_OSS_NE user:'+nsng_oss_configs.NSNG_OSS_database['database'][0]['user']
    print 'NSNG_OSS_NE password:'+nsng_oss_configs.NSNG_OSS_database['database'][0]['password']

    print 'NSNG_OSS_database name:'+nsng_oss_configs.NSNG_OSS_NE['NE'][0]['name']
    print 'NSNG_OSS_database database:'+nsng_oss_configs.NSNG_OSS_NE['NE'][0]['database']
    
