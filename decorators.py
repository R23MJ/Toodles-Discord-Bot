import functools
import discord

def permissions(required_permissions=None, required_roles=None):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            
            perms = ctx.author.guild_permissions
            if required_permissions:
                if all(getattr(perms, perm, False) for perm in required_permissions):
                    return await func(ctx, *args, **kwargs)
            
            if required_roles:
                lowered_roles = [role.lower() for role in required_roles]
                if any(lowered_role in role.name.lower() for lowered_role in lowered_roles for role in ctx.author.roles):
                    return await func(ctx, *args, **kwargs)
            
            embed = discord.Embed(
                title="Error",
                description="You do not have permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        return wrapper
    return decorator