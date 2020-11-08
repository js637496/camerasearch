import "reflect-metadata";
import "dotenv/config";
import express from 'express';
import {ApolloServer} from 'apollo-server-express';
import { buildSchema } from "type-graphql";
import { UserResolver } from "./UserResolver";
import { createConnection } from "typeorm";
import cookieParser from 'cookie-parser';
import { verify } from "jsonwebtoken";
import { User } from './entity/User';
import { createAccessToken, createRefreshToken } from "./auth";
import { sendRefreshToken } from "./sendRefreshToken";
import cors from "cors";
import { CameraResolver } from "./CameraResolver";

(async () => {
    const app = express();

    app.use(
        cors({
            credentials: true,
            origin: "http://localhost:3000"
        })
    );

    app.use(cookieParser());    
    app.get('/', (_req, res) => res.send('hello'));
    app.post('/refresh_token', async (req, res) => {
        const token = req.cookies.jid;
        if (!token) 
        {
            return res.send({ ok: false, accessToken: '' });
        }

        let payload: any = null;
        try {
            payload = verify(token, process.env.REFRESH_TOKEN_SECRET!)

        } catch(err) {
            console.log(err);
            return res.send({ ok: false, accessToken: '' });
        }

        // valid, send access token
        const user = await User.findOne({ id: payload.userId});

        if (!user) {
            return res.send({ ok: false, accessToken: '' });
        }

        if (user.tokenVersion !== payload.tokenVersion) {
            return res.send({ ok: false, accessToken: "" });
        }

        sendRefreshToken(res, createRefreshToken(user));

        return res.send({ ok: true, accessToken: createAccessToken(user) });
    });

    await createConnection();

    const apolloServer = new ApolloServer({
        schema: await buildSchema({
            resolvers: [UserResolver, CameraResolver]
        }),
        context: ({ req, res }) => ({ req, res })
    });

    apolloServer.applyMiddleware({ app, cors: false });

    app.listen(4001, () => {
        console.log("Express server started");
    });

})();
