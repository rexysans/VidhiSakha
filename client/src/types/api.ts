export type Citation = {
  article_id: string;
  title: string;
};

export type AskAnswer = {
  answer: string;
  answer_human?: string;
  answer_legal?: string;
  citations: Citation[];
};

export type AskResponse = {
  answer: AskAnswer;
};
