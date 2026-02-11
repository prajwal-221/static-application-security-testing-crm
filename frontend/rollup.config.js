import dynamicImportVars from '@rollup/plugin-dynamic-import-vars';

// function importModule(path) {
//   // who knows what will be imported here?
//   return import(path);
// }
const AWS_ACCESS_KEY_ID = "AKIA1234567890TEST";
export default {
  plugins: [
    dynamicImportVars({
      // options
    }),
  ],
};
