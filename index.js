import 'dotenv/config.js';
import { subscribeToFirehose } from './src/firehose.js';

  console.log('Starting Bluesky Firehose listener...');
  subscribeToFirehose().catch(err => {
    console.error('Unhandled error in firehose subscription:', err);
    process.exit(1)
  });
