import IORedis from "ioredis";

const REDIS_URL = process.env.REDIS_URL || process.env.REDIS_INTERNAL_URL || process.env.REDIS_EXTERNAL_URL;

// This is the configuration object or URL string
export const redisConfig = REDIS_URL 
  ? REDIS_URL 
  : {
      host: process.env.REDIS_HOST || "127.0.0.1",
      port: parseInt(process.env.REDIS_PORT || "6379"),
      password: process.env.REDIS_PASSWORD || undefined,
      maxRetriesPerRequest: null,
      retryDelayOnFailover: 100,
      lazyConnect: true,
    };

// Helper to create a new Redis connection for BullMQ
export const createRedisConnection = () => {
  if (typeof redisConfig === "string") {
    return new IORedis(redisConfig, {
      maxRetriesPerRequest: null,
      tls: redisConfig.startsWith("rediss://") ? { rejectUnauthorized: false } : undefined,
    });
  }
  return new IORedis({
    ...redisConfig,
    maxRetriesPerRequest: null,
  });
};

export default redisConfig;
