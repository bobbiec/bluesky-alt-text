import { Subscription } from "@atproto/xrpc-server";
import { cborToLexRecord, readCar } from "@atproto/repo";
import { writeToCsv } from "./storage.js";

const SERVICE = "bsky.network";
const METHOD = "com.atproto.sync.subscribeRepos";
const COLLECTION = "app.bsky.feed.post";
const CREATE_ACTION = "create";

const handleEvent = async (event) => {
  // Only process commit events which have .ops and .blocks
  if (!event.ops || !event.blocks) return;

  try {
    const car = await readCar(event.blocks);
    for (const op of event.ops) {
      if (op.action !== CREATE_ACTION) continue;

      const [collection] = op.path.split("/");
      if (collection !== COLLECTION) continue;

      if (!op.cid) continue;
      const recBytes = car.blocks.get(op.cid);
      if (!recBytes) continue;

      const record = cborToLexRecord(recBytes);

      if (record && record.embed && record.embed.images) {
        const recordsToSave = record.embed.images.map(image => ({
          uri: `at://${event.repo}/${op.path}`,
          altText: image.alt || '',
        }));

        if (recordsToSave.length > 0) {
          await writeToCsv(recordsToSave);
          console.log(`Saved ${recordsToSave.length} image posts from ${event.repo}.`);
        }
      }
    }
  } catch (err) {
    // It's common to see errors here, such as block not found.
    // We can ignore them for this script's purpose.
  }
};

export const subscribeToFirehose = async () => {
  const subscription = new Subscription({
    service: `wss://${SERVICE}`,
    method: METHOD,
    validate: (body) => body,
  });

  console.log("Started subscription to Bluesky Firehose.");

  for await (const event of subscription) {
    handleEvent(event);
  }
};
