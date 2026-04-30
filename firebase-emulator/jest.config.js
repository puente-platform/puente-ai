/** @type {import('jest').Config} */
module.exports = {
  preset: "ts-jest",
  testEnvironment: "node",
  testTimeout: 30000,
  globals: {
    "ts-jest": {
      tsconfig: "./tsconfig.json",
    },
  },
};
