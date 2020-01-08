from discord.ext import commands

def has_role(role_name):
    def predicate(ctx):
        roles = [role.name for role in ctx.message.author.roles]
        return role_name in roles
    return commands.check(predicate)

def has_role_id(role_id):
    def predicate(ctx):
        roles = [role.id for role in ctx.message.author.roles]
        return role_id in roles
    return commands.check(predicate)

def in_guild(guild_id):
    def predicate(ctx):
        return guild_id == ctx.message.guild.id

def debug():
    def predicate(ctx):
        print(ctx.__dict__)
        return True
    return commands.check(predicate)
