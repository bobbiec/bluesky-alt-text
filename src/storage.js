import { createObjectCsvWriter } from 'csv-writer';
import fs from 'fs';

const csvWriter = createObjectCsvWriter({
  path: 'image_posts.csv',
  header: [
    {id: 'uri', title: 'POST_URI'},
    {id: 'altText', title: 'ALT_TEXT'},
  ],
  append: true,
});

export const writeToCsv = async (records) => {
  if (!fs.existsSync('image_posts.csv')) {
    await csvWriter.writeRecords([]); // Creates file with header
  }
  await csvWriter.writeRecords(records);
};