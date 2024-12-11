CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name text NOT NULL,
  email text NOT NULL,
  location text[] NOT NULL,
  password text NOT NULL,
  skills text[],
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  desired_salary_min int,
  desired_salary_max int,
  desired_salary_currency text
);

INSERT INTO users (name, email, location, password, skills, desired_salary_min, desired_salary_max, desired_salary_currency)
VALUES ('John Doe', 'email@email.com', '{New York, NY}', 'password', '{Python, JavaScript}', 100000, 150000, 'USD');