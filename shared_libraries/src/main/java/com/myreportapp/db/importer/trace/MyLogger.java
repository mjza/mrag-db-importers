package com.myreportapp.db.importer.trace;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MyLogger {
    private static MyLogger instance;
    private final Logger logger;

    private MyLogger(Class<?> clazz) {
        this.logger = LoggerFactory.getLogger(clazz);
    }

    public static synchronized MyLogger getInstance(Class<?> clazz) {
        if (instance == null) {
            instance = new MyLogger(clazz);
        }
        return instance;
    }

    public void info(String message) {
        logger.info(message);
    }

    public void error(String message, Throwable throwable) {
        logger.error(message, throwable);
    }

    public void debug(String message) {
        logger.debug(message);
    }

    public void warn(String message) {
        logger.warn(message);
    }

    public void trace(String message) {
        logger.trace(message);
    }
}

