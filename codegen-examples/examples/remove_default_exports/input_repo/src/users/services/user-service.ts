// Original file keeps default export
import User from '../models/user';

export default class UserService {
    getUser(id: string): User {
        return { id, name: 'John', email: 'john@example.com' };
    }
}
