// src/routes/summary/[file_id]/+page.ts
import type { PageLoad } from './$types';

export const load: PageLoad = ({ params }) => {
  return {
    fileId: params.file_id
  };
};
