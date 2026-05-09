export type LoginResponse = {
  access_token: string;
  token_type: string;
};

export type RegisterPayload = {
  name: string;
  surname: string;
  email: string;
  password: string;
  is_active: boolean;
};
