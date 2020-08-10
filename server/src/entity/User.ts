import {Entity, PrimaryGeneratedColumn, Column, BaseEntity} from "typeorm";
import { ObjectType, Field, Int } from "type-graphql";

@ObjectType()
@Entity('users')
export class User extends BaseEntity {
    @Field(() => Int)
    @PrimaryGeneratedColumn()
    id: number;

    @Field()
    @Column("text")
    email: string;

    @Field(() => Int)
    @Column("int", {nullable: true, default: 0})
    securityLevel: number;

    @Column("text")
    password: string;

    @Column("int", {default: 0})
    tokenVersion: number;
}
