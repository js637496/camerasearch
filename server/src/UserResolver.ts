import {Resolver, Query, Mutation, Arg, ObjectType, Field, Ctx, UseMiddleware, Int} from 'type-graphql';
import { User } from './entity/User';
import { hash, compare } from 'bcryptjs';
import { MyContext } from './MyContext';
import { createRefreshToken, createAccessToken } from './auth';
import { isAuth } from './isAuth';
import { sendRefreshToken } from './sendRefreshToken';
import { getConnection } from 'typeorm';
import { verify } from 'jsonwebtoken';

@ObjectType()
class LoginResponse {
    @Field()
    accessToken: string;
    @Field(() => User)
    user: User;
};

@Resolver()
export class UserResolver {
    @Query (() => [User])
    users() {
        return User.find();
    }

    @Query(() => User, { nullable: true })
    me(
        @Ctx() context: MyContext
    ) {
        const authorization = context.req.headers['authorization'];

        if (!authorization) {
            return null;
        }

        try {
            const token = authorization?.split(' ')[1];
            const payload: any = verify(token, process.env.ACCESS_TOKEN_SECRET!);
            return User.findOne(payload.userId)

        } catch(err) {
            console.log(err);
            return null;
        }
    }

    @Query(() => String)
    hello(){
        return 'hi!';
    }
    
    @Query(() => String)
    @UseMiddleware(isAuth)
    bye(
        @Ctx() {payload}: MyContext
    ) {
        console.log(payload);
        return `your user id is ${payload!.userId}`;
    }

    @Mutation(() => Boolean)
    async logout(@Ctx() {res}: MyContext) {
        sendRefreshToken(res, "");
        return true;
    }

    @Mutation(() => Boolean)
    async revokeRefreshTokensForUser(
        @Arg("userId", () => Int) userId: number) {
        await getConnection()
            .getRepository(User)
            .increment({ id: userId }, "tokenVersion", 1);
        return true;
    }

    @Mutation(() => LoginResponse)
    async login(
        @Arg('email', () => String) email: string,
        @Arg('password', () => String) password: string,
        @Ctx() {res}: MyContext
    ): Promise<LoginResponse> {

        const user = await User.findOne({ where: { email } });

        if (!user)
        {
            throw new Error("Invalid username or password");
        }

        const valid = await compare(password, user.password);

        if (!valid)
        {
            throw new Error("Invalid username or password");
        }
        
        // logged in

        sendRefreshToken(res, createRefreshToken(user));

        return {
            accessToken: createAccessToken(user),
            user: user
        };
    }
    
    @Mutation(() => Boolean)
    async register(
        @Arg('email', () => String) email: string,
        @Arg('password', () => String) password: string
    ) {

        const hashedPassword = await hash(password, 12);

        try {
            await User.insert({
                email,
                password: hashedPassword
            });
        } catch (err) {
            console.log(err);
            return false;
        }

        return true;
    }
}