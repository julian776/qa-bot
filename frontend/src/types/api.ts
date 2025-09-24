export interface QAExample {
  question: string;
  answer: string;
}

export interface QAExamplesResponse {
  examples: QAExample[];
}

export interface QARequest {
  question: string;
}

export interface QAResponse {
  id: number;
  question: string;
  answer: string;
}
