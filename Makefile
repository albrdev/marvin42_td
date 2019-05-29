DIR_SRC				:= .
DIR_CFG				:= cfg

DIR_BIN_INSTALL		:= /usr/local/bin
DIR_CFG_INSTALL		:= /etc

TD_SRC_NAME			:= marvin42_td.py
TD_APP_NAME			:= $(basename $(TD_SRC_NAME))
TD_CFG_NAME			:= $(TD_APP_NAME)rc

CGD_SRC_NAME		:= marvin42_cgd.py
CGD_APP_NAME		:= $(basename $(CGD_SRC_NAME))
CGD_CFG_NAME		:= $(CGD_APP_NAME)rc

MOD_NAME			:= modules

CMD_CP				:= cp
CMD_RM				:= rm
CMD_CHMOD			:= chmod
CMD_PRINT			:= @printf

.PHONY: install
install:
	$(CMD_CP) --force $(DIR_SRC)/$(TD_SRC_NAME) $(DIR_BIN_INSTALL)/$(TD_APP_NAME)
	$(CMD_CP) --no-clobber $(DIR_CFG)/$(TD_CFG_NAME) $(DIR_CFG_INSTALL)

	$(CMD_CP) --force $(DIR_SRC)/$(CGD_SRC_NAME) $(DIR_BIN_INSTALL)/$(CGD_APP_NAME)
	$(CMD_CP) --no-clobber $(DIR_CFG)/$(CGD_CFG_NAME) $(DIR_CFG_INSTALL)

	$(CMD_CP) --recursive --no-target-directory --force $(DIR_SRC)/$(MOD_NAME) $(DIR_BIN_INSTALL)/$(MOD_NAME)

	$(CMD_CHMOD) u+x,g+x $(DIR_BIN_INSTALL)/$(TD_APP_NAME)
	$(CMD_CHMOD) u+x,g+x $(DIR_BIN_INSTALL)/$(CGD_APP_NAME)

.PHONY: uninstall
uninstall:
	$(CMD_RM) --recursive --force $(DIR_BIN_INSTALL)/$(MOD_NAME)
	$(CMD_RM) --force $(DIR_BIN_INSTALL)/$(TD_APP_NAME)
	$(CMD_RM) --force $(DIR_BIN_INSTALL)/$(CGD_APP_NAME)
