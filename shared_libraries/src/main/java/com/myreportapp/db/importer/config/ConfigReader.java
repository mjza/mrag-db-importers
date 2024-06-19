package com.myreportapp.db.importer.config;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.Properties;
import com.fasterxml.jackson.databind.ObjectMapper;

public class ConfigReader {
	
	private static ConfigReader instance;
	private Config config;
	private Properties properties;
	
	private ConfigReader(String jsonMappingFile, String dbConfigFile) {
        config = readColumnMapping(jsonMappingFile);
        properties = readDbConfig(dbConfigFile);
    }
	
	public static synchronized ConfigReader getInstance(String jsonMappingFile, String dbConfigFile) {
        if (instance == null) {
            instance = new ConfigReader(jsonMappingFile, dbConfigFile);
        }
        return instance;
    }
	
	public static synchronized ConfigReader getInstance() {        
        return instance;
    }
	
	private Config readColumnMapping(String jsonFile) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            return mapper.readValue(new File(jsonFile), Config.class);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
	
	private Properties readDbConfig(String dbConfigFile) {
        Properties props = new Properties();
        try (BufferedReader reader = new BufferedReader(new FileReader(dbConfigFile))) {
            props.load(reader);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return props;
    }

	public Config getConfig() {
		return config;
	}

	public Properties getProperties() {
		return properties;
	}
}
